
class Knowledge_Filter:

    def __init__(self):
        pass

    def filter(self, terms):
        for elem in terms.data.keys():
            terms.filtered_data[elem] = {}
            [terms.filtered_data[elem].update({i: []}) for i in range(4)]

        placement = {"wikidata":2, "dbpedia":3, "special": 4, "web_search":0}

        for id in terms.data:
            for source in terms.data[id]:
                for trip in terms.data[id][source]:
                    if source in placement and  (terms.term == trip[0] or terms.term == trip[2]):
                        if placement[source] in [2, 3]:
                            terms.filtered_data[id][placement[source]].append(trip)
                        elif len(trip) == 3:
                            terms.filtered_data[id][placement[source]].append(trip)

        '''
        for key_id in terms.data:
            for key_source in terms.data[key_id]:
                if key_source != 'wikidata' and key_source != 'dbpedia':
                    for tup in terms.data[key_id][key_source]:
                        if len(tup) == 3:
                            if terms.term in tup[0] or terms.term in tup[2]:
                                if key_id in terms.filtered_data:
                                    terms.filtered_data[key_id][0].append(tup)
                                else:
                                    terms.filtered_data[key_id] = {0:[], 1:[]}
                                    terms.filtered_data[key_id][0].append(tup)
                            else:
                                if key_id in terms.filtered_data:
                                    terms.filtered_data[key_id][1].append(tup)
                                else:
                                    terms.filtered_data[key_id] = {0:[], 1:[]}
                                    terms.filtered_data[key_id][1].append(tup)
            if key_id in terms.filtered_data:
                if 'wikidata' in terms.filtered_data[key_id]:
                    terms.filtered_data[key_id][2] = terms.data[key_id]['wikidata']
                if 'dbpedia' in terms.filtered_data[key_id]:
                    terms.filtered_data[key_id][3] = terms.data[key_id]['dbpedia']
            else:
                terms.filtered_data[key_id] = {0:[], 1:[], 2:terms.data[key_id]['wikidata'] if 'wikidata' in terms.data[key_id] else [], 3:terms.data[key_id]['dbpedia'] if 'dbpedia' in terms.data[key_id] else []}
        '''
