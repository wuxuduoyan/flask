from redis import *

if __name__ == '__main__':

    sr = StrictRedis(host='localhost', port=6379, db=0,decode_responses=True)
    # 以上可以简写为
    # sr=StrictRedis()
    try:
        result = sr.set('name', 'itheima')
        res=sr.get('name')
        print(res)
    except Exception as e:
        print(e)
