import pickle

d = {'time': 242324.8679803919,
'shoots': 50464,
'done damage': 243391.5,
'received damage': 155747.16666666695,
'time on ground':1,
'time in air':1}
pickle.dump(d, open('stats.p','wb'))
print(pickle.load(open('stats.p','rb')))