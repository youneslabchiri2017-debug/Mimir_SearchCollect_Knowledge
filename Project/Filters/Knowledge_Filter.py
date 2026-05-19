
class Knowledge_Filter:

    def __init__(self):
        pass

    def filter(self, terms):
        for key_id in terms.data:
            for key_source in terms.data[key_id]:
                if key_source != 'wikidata':
                    for tup in terms.data[key_id][key_source]:
                        if len(tup) == 3:
                            if terms.term in tup[0] or terms.term in tup[2]:
                                if key_id in terms.filtered_data:
                                    terms.filtered_data[key_id][0].append(tup)
                                else:
                                    terms.filtered_data[key_id] = {0:[], 1:[]}
                            else:
                                if key_id in terms.filtered_data:
                                    terms.filtered_data[key_id][1].append(tup)
                                else:
                                    terms.filtered_data[key_id] = {0:[], 1:[]}
            if key_id in terms.filtered_data:
                terms.filtered_data[key_id][2] = terms.data[key_id]['wikidata']
            else:
                terms.filtered_data[key_id] = {0:[], 1:[], 2:terms.data[key_id]['wikidata']}
