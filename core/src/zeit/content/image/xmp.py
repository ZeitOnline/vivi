def extract_metadata(xmp):
    result = {'title': None, 'copyright': None, 'caption': None}
    if 'xapmeta' in xmp:
        data = xmp['xapmeta']
        data = data.get('RDF', {}).get('Description', {})
        if isinstance(data, dict):
            data = (data,)
        for item in data:
            if 'Headline' in item:
                result['title'] = item['Headline']
            if 'creator' in item:
                result['creator'] = item['creator'].get('Seq', {}).get('li', None)
            if 'Credit' in item:
                result['credit'] = item['Credit']
            if 'description' in item:
                result['caption'] = (
                    item.get('description', {}).get('Alt', {}).get('li', {}).get('text', None)
                )
    if 'xmpmeta' in xmp:
        data = xmp['xmpmeta']
        data = data.get('RDF', {}).get('Description', {})
        if isinstance(data, dict):
            data = (data,)
        for item in data:
            if 'Headline' in item:
                result['title'] = item['Headline']
            if 'creator' in item:
                result['creator'] = item['creator'].get('Seq', {}).get('li', None)
            if 'Credit' in item:
                result['credit'] = item['Credit']
            if 'description' in item:
                result['caption'] = (
                    item.get('description', {}).get('Alt', {}).get('li', {}).get('text', None)
                )

    if 'credit' in result or 'creator' in result:
        result['copyright'] = '/'.join(
            filter(None, (result.get('creator', None), result.get('credit', None)))
        )
        if 'credit' in result:
            del result['credit']
        if 'creator' in result:
            del result['creator']
    return result
