import pickle

d = {
    'time':640.137000000083,
    'shoots':0,
    'done damage':0,
    'received damage':0,
}
pickle.dump(d, open('stats.p','wb'))
print(pickle.load(open('stats.p','rb')))