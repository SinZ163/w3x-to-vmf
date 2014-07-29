
def print_headers(mpyqArc_instance):
    print("MPQ archive header")
    print("------------------")
    for key, value in mpyqArc_instance.header.iteritems():
        if key == "user_data_header":
            continue
        print("{0:30} {1!r}".format(key, value))
    if mpyqArc_instance.header.get('user_data_header'):
        print()
        print("MPQ user data header")
        print("--------------------")
        for key, value in mpyqArc_instance.header['user_data_header'].iteritems():
            print("{0:30} {1!r}".format(key, value))
    print()

def print_hash_table(mpyqArc_instance):
    print("MPQ archive hash table")
    print("----------------------")
    print(" Hash A   Hash B  Locl Plat BlockIdx")
    for entry in mpyqArc_instance.hash_table:
        print('{0:0>8X} {1:0>8X} {2:0>4X} {3:0>4X} {4:0>8X}'.format(*entry))
    print()

def print_block_table(mpyqArc_instance):
    print("MPQ archive block table")
    print("-----------------------")
    print(" Offset  ArchSize RealSize  Flags")
    for entry in mpyqArc_instance.block_table:
        print('{0:0>8X} {1:>8} {2:>8} {3:>8X}'.format(*entry))
    print()

def print_files(mpyqArc_instance):
    if mpyqArc_instance.files:
        print("Files")
        print("-----")
        width = max(len(name) for name in mpyqArc_instance.files) + 2
        for filename in mpyqArc_instance.files:
            hash_entry = mpyqArc_instance.get_hash_table_entry(filename)
            block_entry = mpyqArc_instance.block_table[hash_entry.block_table_index]
            print("{0:{width}} {1:>8} bytes".format(filename.decode(),
                                                    block_entry.size,
                                                    width=width))