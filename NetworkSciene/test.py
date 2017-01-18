d ={ 12:1, 13:1, 14:1,16:1, 17:2, 18:2, 19:1}
infected = [1,3]
print([x for d[x] in d if d[x] not in infected] )

