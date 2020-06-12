import random
import time

from conf import getPTConnection


class MysqlUntileFunction(object):

    def createDB(self):
        list = ['qijia','tubatu']
        for x in list:
            if 'qijia' == x:
                sql = 'CREATE TABLE IF NOT EXISTS spider_qijia(' \
                      'id INT PRIMARY KEY AUTO_INCREMENT, ' \
                      'companyName VARCHAR(200) NOT NULL,' \
                      'case_num VARCHAR(250),' \
                      'work_num VARCHAR(250),' \
                      'foreman VARCHAR(250),' \
                      'href_params TEXT,' \
                      'stylist_num VARCHAR(250),' \
                      'city VARCHAR(250))'
            else:
                sql = 'CREATE TABLE IF NOT EXISTS spider_tubatu(' \
                      'id INT PRIMARY KEY AUTO_INCREMENT, ' \
                      'city VARCHAR(200) NOT NULL,' \
                      'mole VARCHAR(250),' \
                      'companyName VARCHAR(250),' \
                      'address VARCHAR(250),' \
                      'phone TEXT,' \
                      'desgin_number VARCHAR(250),' \
                      'decoration_number VARCHAR(250),'\
                      'type_key VARCHAR(250))'
            with getPTConnection() as db:

                db.cursor.execute(sql)
                db.conn.commit()

    def savaMysqlDB(self, item, type='qijia'):
        while 1:
            try:
                with getPTConnection() as db:
                    if type == 'qijia':
                        sql = 'insert into {}(companyName,case_num,work_num,foreman,stylist_num,href_params,city) values(%s,%s,%s,%s,%s,%s,%s)'.format('spider_qijia')
                        params = (item['companyName'],
                                  item['case_num'],
                                  item['work_num'],
                                  item['foreman'],
                                  item['stylist_num'],
                                  item['href_params'],
                                  item['city'],
                                  )
                    else:
                        sql = 'insert into {}(city,mole,companyName,address,phone,desgin_number,decoration_number,type_key) values(%s,%s,%s,%s,%s,%s,%s,%s)'.format('spider_tubatu')
                        params = (item['city'],
                                  item['mole'],
                                  item['companyName'],
                                  item['address'],
                                  item['phone'],
                                  item['desgin_number'],
                                  item['decoration_number'],
                                  item['type_key'],
                                  )
                    try:
                        db.cursor.execute(sql, params)
                        db.conn.commit()
                        print('##############入库成功{}############'.format(params))
                        break
                    except Exception as e:
                        print(e)
            except Exception as e:
                time.sleep(random.randint(2,3))
                print(e)


if __name__ == '__main__':
    mysqluntil = MysqlUntileFunction()
    mysqluntil.createDB()