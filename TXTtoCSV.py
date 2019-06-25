'''
Last updated Monday June 24, 2019
Author: Noah D'Souza
Designed and tested on Python 3.6.3
'''

def TXTtoCSV(text, output):
    # text is the name of the SoEx output text file
    # output is the output csv filepath/name
    # This function parses and forms a csv table of all the data from a Source
    # Extractor output txt file. It separates the header and data, uses the
    # replaceChar helper function to clean up the contents of each
    import csv
    from flagConverter import flagConverter
    with open(text, 'r') as infile:
        lines = infile.readlines()
        header = []
        data = []
        # put text in respective header and data lists
        for i in range(len(lines)):
            if lines[i][0] == '#':
                header.append(lines[i])
            else:
                data.append(lines[i])
        # replace excess spacing with _ or ,
        for j in range(len(header)):
            header[j] = replaceChar(header[j].rstrip("\r\n"),' ','_')
        flagind = header.index('#_2_FLAGS_Extraction_flags_')
        for k in range(len(data)):
            data[k] = replaceChar(data[k].rstrip("\r\n"),' ',',')
        # turn data into a 2D array
        array = []
        count = 0
        for p in range(len(data)-1):
            ap = list(data[p].split(','))
            ap.pop(0)
            # 1, 2, and 16 appear most common?
            if not any(i in ['1','2','4','8','16','32','64','128'] for i in
                flagConverter(ap[1])):
                ap[0] = count+1
                array.append(ap)
                count+=1
        # write a csv with header as the column titles and the data as rows
        with open(output,'w') as new_csv:
            csvWriter = csv.writer(new_csv,delimiter=',')
            csvWriter.writerow(header)
            csvWriter.writerows(array)
        return(output)

def replaceChar(block, r, n):
    # str is the string being modified
    # r is the character being replaced in blocks
    # n is the character replacing variable blocks of r
    # all instances of r replaced by n
    block = block.replace(r,n)
    # all instances of nn replaced by n dynamically (bottom-up)
    while n+n in block:
        block = block.replace(n+n,n)
    return block
