for i in range(143) :
    number = i
    formatted_number = f"{number:03}"
    print(formatted_number)  # Output: '011'
    all_contents = open('tilemap_' + formatted_number + '.arr', 'r').readlines()
    file_out = open('converted/' + 'map_' + formatted_number + '.json', 'w')
    file_out.write('{\n')
    file_out.write('    "tilemap": {\n')
    file_out.write('        "W": 32,\n')
    file_out.write('        "H": 22,\n')
    file_out.write('        "tilemap": [\n')
    for iLine in range(2, 24) :
        file_out.write('            ')
        file_out.write(all_contents[iLine].replace(' 0', ' ').replace(' ', ', '))
    file_out.write('        ]\n')
    file_out.write('    }\n')
    file_out.write('}')
    