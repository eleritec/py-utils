import ldap
from enum import Enum
from general import first, usable, flatten, get_logger, first_match, lsplit

class ADEntryMap:
    def __init__(self, *field_mappings):
        self.mapping = {}
        self.map('distinguishedName->dn')
        self.map(*field_mappings)

    def map(self, *mappings): 
        field_type = first_match(mappings, lambda item: type(item) is FieldType, FieldType.STRING)
        field_mappings = [mapping for mapping in mappings if type(mapping) is str]
        mapper = ad_as_list if field_type==FieldType.LIST else ad_as_single
        return self.add_mappings(mapper, field_mappings)

    def add_mappings(self, mapper, mappings):
        for mapping in mappings:
            pair = mapping.split('->')
            from_name = pair[0].strip()
            to_name = pair[1].strip() if len(pair) > 1 else from_name
            self.add_mapping(from_name, to_name, mapper)
        return self

    def add_mapping(self, from_name, to_name=None, mapper=None):
        mapper = mapper if mapper else ad_as_single
        to_name = to_name if to_name else from_name
        self.mapping[from_name] = (to_name, mapper)
        return self

    def parse_entry(self, entry):
        record = {}
        for from_name in self.mapping.keys():
            to_name = self.mapping[from_name][0]
            parser = self.mapping[from_name][1]
            record[to_name] = parser(entry, from_name)
        return record

    def parse_results(self, results_list):
        return [self.parse_entry(record_tuple[1]) for record_tuple in results_list]

class ADQuery:
    def __init__(self, conn, base, filter=None, scope=ldap.SCOPE_SUBTREE):
        self.logger = get_logger(self)
        self.conn = conn
        self.base = base
        self.filter = filter
        self.scope = scope
        self.entry_mapping = None

    def search(self, ad_filter=None):
        _filter = ad_filter if ad_filter else self.filter
        if not _filter:
            return []

        filter_text = _filter[0:100] if len(_filter) > 100 else _filter
        self.logger.info('Searching[%s] for \n\t%s...', self.base, filter_text)

        results = None
        try:
            results = self.conn.search_s(self.base, self.scope, _filter)
        except ldap.FILTER_ERROR as e:
            self.logger.error(e)
            self.logger.error(ad_filter.replace(')(', ')\n('))
            results = []

        return self.entry_mapping.parse_results(results) if self.entry_mapping else results

    def map_results(self, *field_mappings):
        self.get_entry_map().map(*field_mappings)
        return self

    def get_entry_map(self):
        if not self.entry_mapping:
            self.entry_mapping = ADEntryMap()
        return self.entry_mapping


class DNQuery(ADQuery):
    def __init__(self, conn, base, type_filter, dn_list, block_size=1000, scope=ldap.SCOPE_SUBTREE):
        super().__init__(conn, base, None, scope)

        self.block_size = max(1, block_size)
        self.target_dns = [dn for dn in dn_list if self.is_target_dn(dn)] if dn_list else []
        self.filter = '(&(' + type_filter + ')(|{}))'

    def is_target_dn(self, dn):
        return dn and dn.endswith(self.base)

    def has_targets(self):
        return len(self.target_dns) > 0

    def search(self):
        if not self.has_targets():
            return []
        return self.search_block(self.target_dns)[0] if self.block_size < 1 else self.search_blocks()

    def search_blocks(self):
        results, missing = [], []
        
        counter = 1
        blocks = lsplit(self.target_dns, self.block_size)
        for block in blocks:
            found, found_dns = self.search_block(block)
            results.extend(found)
            missing.extend([dn for dn in block if dn not in found_dns])

            self.logger.info('Retrieved %d of %d records in block [%d:%d].', len(found), len(block), counter, len(blocks))
            counter = counter + 1

        if len(missing) > 0:
            self.logger.warn("Referenced entries not found in AD:\n" + '\n'.join(missing))

        return results

    def search_block(self, dn_block):
        ad_filter = self.filter.format(to_clause('distinguishedName={}', escape_filter(dn_block)))
        results = super().search(ad_filter) if dn_block else []
        return results, set([record['dn'] for record in results])
    

class FieldType(Enum):
    STRING = 1
    LIST = 2

def ad_as_single(entry, attr):
    raw_value = entry.get(attr, None) if attr else None
    if raw_value is None:
        return ''

    decoded = decode_bytes(raw_value)
    return first(decoded) if type(decoded) is list else decoded

def ad_as_list(entry, attr):
    raw_value = entry.get(attr, None) if attr else None
    if raw_value is None:
        return []

    decoded = decode_bytes(raw_value)
    list_value = decoded if type(decoded) is list else [decoded]    
    list_value = list_value if list_value is not None else []
    return usable(list_value)

def escape_filter(value):
    if value is None:
        return value

    if type(value) is list:
        return [escape_filter(word) for word in value]

    return value.replace('\\', '\\\\').replace('(', '\(').replace(')', '\)')

def ad_connect(username, password, hosts):
    valid, message = validate_connect(username, password, hosts)
    if not valid:
        return None, message

    hosts = get_valid_hosts(hosts)
    host = first(hosts)

    address = 'ldap://{}'.format(host)
    conn = ldap.initialize(address)
    conn.protocol_version = 3
    conn.set_option(ldap.OPT_REFERRALS, 0)

    try:
        conn.simple_bind_s(username, password)
        return conn, 'Succesfully authenticated to {}'.format(address)
    except ldap.INVALID_CREDENTIALS:
        return None, 'Invalid credentials for {} on {}'.format(username, address)
    except ldap.SERVER_DOWN:
        next_hosts = hosts[1:]
        if next_hosts:
            get_logger().warn('Server is down at %s.  Trying next host...', address)
            return ad_connect(username, password, next_hosts)
        return None, 'Server is down at {}'.format(address)
    except ldap.LDAPError as e:
        if type(e.message) == dict and e.message.has_key('desc'):
            return None, 'LDAP Error: ' + e.message['desc']
        return None, 'LDAP Error: ' + e

    return conn

def validate_connect(username, password, hosts):
    host = first(get_valid_hosts(hosts))
    if not host:
        return False, 'Unable to resolve an AD host address'
    if not username:
        return False, 'Unable to resolve an AD username'
    if not password:
        return False, 'Unable to resolve an AD password'
    return True, ''

def get_valid_hosts(hosts):
    return usable(hosts)

def to_clause(*criteria):
    values = collect_clause_values(*criteria)
    return ''.join([wrap_criteria(value) for value in values])

def wrap_criteria(value):
    value = value.strip()
    if not value.startswith('('):
        value = '(' + value
    if not value.endswith(')'):
        value = value + ')'
    return value

def collect_clause_values(*criteria):
    criteria = [item.strip() for item in flatten(criteria) if item and item.strip()]
    if not criteria:
        return []

    if len(criteria) == 1 or '{}' not in criteria[0]:
        return criteria

    pattern = criteria[0]
    criteria.remove(pattern)
    return [pattern.format(value) for value in criteria]

def decode_bytes(data):
    if type(data) is bytes:
        return data.decode('utf-8')

    if type(data) is list:
        return [decode_bytes(entry) for entry in data]

    return data
