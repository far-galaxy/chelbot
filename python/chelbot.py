# -*- coding: utf-8 -*-
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import dropbox
from time import sleep
from math import ceil

# API-ключ созданный ранее
token = "7560f20b89726ae98bf473d4e03ebd7ee9e80407f8ba9bb11a976e1509c937ab1c330806d365116574ca2"

# Авторизуемся как сообщество
vk = vk_api.VkApi(token=token)
dbx = dropbox.Dropbox('BL_ESSG-vAAAAAAAAAAAD0gNKClnYQQ7m-ZaNfv_sgmhGp15GOvlnGcu-SsvnuDD')
print("ChelBot ready!")

# Работа с сообщениями
longpoll = VkLongPoll(vk)

debug = False

state = {'menu':0, 'add':1, 'read':2, 'calc':3, 'add_mark':4, 'sub_mark':5, 'del_subj':6, 'del':7}
mark_d = {2:"двойку", 3:"тройку", 4:"четвёрку", 5:"пятёрку"}

name_marks=[[' двоек',' двойку',' двойки',' двойки', ' двойки',' двоек'],
   [' троек',' тройку',' тройки',' тройки', ' тройки', ' троек'],
   [' четвёрок',' четвёрку',' четвёрки',' четвёрки', ' четвёрки',' четвёрок'],
   [' пятёрок',' пятёрку',' пятёрки',' пятёрки', ' пятёрки',' пятёрок']]

mode = 0
nums_subj = 0

# Отправка сообщения без клавиш
def msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'random_id': get_random_id(),'message': message, 'keyboard': open('empty.json', "r", encoding="UTF-8").read()})

# Отправка сообщения с клавишам
def msg_key(user_id, message, key):
    vk.method('messages.send', {'user_id': user_id, 'random_id': get_random_id(),'message': message, 'keyboard': open(key, "r", encoding="UTF-8").read()})

def dbx_upload(name):
    with open(name,'rb') as f: # открываем файл в режиме чтение побайтово
        response = dbx.files_upload(f.read(),'/'+name, mode=dropbox.files.WriteMode.overwrite) # загружаем файл: первый аргумент (file.read()) - какой файл; второй - название, которое будет присвоено файлу уже на дропбоксе.
        #print(response) # выводим результат загрузки

def dbx_read(name):
    try:
        dbx.files_download_to_file(name, '/'+name)
    except:
        msg(event.user_id, "Ой, какая-то ошибка при чтении данных с сервера! Возможно, у вас нет аккаунта. Напиши Начать, чтобы создать его")

def calc_mark(summ, k, positive, okrg, mark):
    count = 0
    while (summ*1.0/k) <= (positive-1+(okrg*1.0/10)):
        summ+=mark
        k+=1
        count+=1
    return count

def constrain(c,mn,mx):
    if c<mn: return mn
    elif c>mx: return mx
    else: return c

def word(number):
    if 1<=number<=20: return constrain(number%20,0,5)
    else: return constrain(number%10,0,5)

def read(file, x, y):
    plin = open(file, 'r')
    lst = [[str(int(plin.readline()))]]
    i = 1
    for line in plin:
        lst.append(line.split(";"))
        if i == y: return lst[i][x]
        i+=1

    plin.close()

def replace(file, x, y, txt):
    plin = open(file, 'r')
    lst = [[str(int(plin.readline()))]]
    i = 1
    for line in plin:
        lst.append(line.split(";"))
        if i == y: lst[i][x] = str(txt)
        lst[i][-1] = lst[i][-1].replace("\n","")
        i+=1

    #print(lst)
    plin.close()
    plin = open(file, 'w')
    plin.write(str(lst[0][0]))
    for l in lst[1:]:
        plin.write("\n"+';'.join(l))
    plin.close()

def delete(file, y):
    plin = open(file, 'r')
    lst = [[str(int(plin.readline()))]]
    i = 1
    for line in plin:
        lst.append(line.split(";"))
        lst[i][-1] = lst[i][-1].replace("\n","")
        i+=1
    lst.pop(y)
    #print(lst)
    plin.close()
    plin = open(file, 'w')
    plin.write(str(lst[0][0]))
    for l in lst[1:]:
        plin.write("\n"+';'.join(l))
    plin.close()


# Основной цикл
for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW and ((event.user_id!=225744535 and debug)):
        msg(event.user_id, "Бот включен, но находится в стадии отладки. Перезвоните позже" )

    # Если пришло новое сообщение
    if event.type == VkEventType.MESSAGE_NEW and ((event.user_id==225744535 and debug) or not debug):

        # Если оно имеет метку для меня (то есть бота)
        if event.to_me:

            # Сообщение от пользователя
            request = event.text
            uid = event.user_id
            #print(request)

            # Каменная логика ответа
            if request == u"Главная":
                msg_key(event.user_id, "Привет! Ты на главной странице!", "list.json")
                mode = state['menu']

            elif request == u"Начать":
                msg(event.user_id, "Привет! Я Чел, главный герой одноимённой игры."
                "Я могу вести твой личный дневник, который ещё и может подсчитать,"
                "сколько тебе нужно заработать оценок, чтобы получить хорошую четвертную оценку.")
                sleep(4)
                msg(event.user_id, "Данные хранятся на сервере и привязаны к вашему аккаунту ВК,"
                    "благодаря чему они никуда не пропадут, даже если вы удалите этот чат.\n"
                    "Сейчас мы проверим, есть ли у тебя какие-то данные на сервере")
                sleep(3)
                try:
                    dbx.files_download_to_file(str(uid)+'.txt', '/'+str(uid)+'.txt')
                except:
                    msg_key(event.user_id, "У тебя пока ничего нет. Нажми кнопку, чтобы создать новый профиль", "akk_new.json")
                else:
                    msg_key(event.user_id, "У тебя уже есть профиль. Можешь оставить его или создать новый (старый будет удалён!)", "akk.json")


            elif request == u"Оставить старый":
                msg_key(event.user_id, "С возвращением!", "list.json")

            elif request == u"Создать новый профиль":
                msg(uid, "Минуточку, создаю профиль")
                plin = open(str(uid)+'.txt', 'w')
                plin.write(str(uid))
                plin.close()
                dbx_upload(str(uid)+'.txt')
                dbx_read(str(uid)+'.txt')
                plin = open(str(uid)+'.txt', 'r')
                fid = int(plin.readline())

                dbx_read('users.txt')
                users = open('users.txt', 'r')
                if users.read().find(str(uid))==-1:
                    users.close()
                    users = open('users.txt', 'a')
                    users.write(str(uid)+";")
                users.close()
                dbx_upload('users.txt')
                print(str(fid)+" registered!")
                if fid==uid:
                    plin.close()
                    msg_key(uid, "Профиль создан успешно! Твой ID: "+str(uid), "list.json")

            elif request == u"Добавить предмет":
                msg_key(uid, "Напиши через пробелы: название предмета, "
                        "текущие оценки без пробелов и степень злости учителя от 1 до 9, "
                        "т.е. десятая доля округления оценки (например, Русский 221 9)", "cancel.json")

                mode = state['add']

            elif mode == state['add'] and request != u"Отмена":
                #Проверка
                txt = request.split()
                if len(txt)!=3:
                    msg_key(uid, "Данные введены неверно. Попробуй ещё раз", "cancel.json")

                else:
                    for i in txt[1]:
                        if int(i)<1 and int(i)>5:
                            msg_key(uid, "Введены некорректные оценки. Попробуй ещё раз", "cancel.json")
                            break
                    else:
                        if not (1<=int(txt[2])<=9):
                            msg_key(uid, "Введена некорректная степень злости учителя. Попробуй ещё раз", "cancel.json")
                        else:
                            #Запись
                            dbx_read(str(uid)+'.txt')
                            plin = open(str(uid)+'.txt', 'a')
                            tmp = request.split()
                            plin.write("\n"+";".join(tmp))
                            plin.close()
                            dbx_upload(str(uid)+'.txt')
                            msg_key(uid, "Данные успешно сохранены!", "list.json")
                            mode = state['menu']

            elif request == u"Отмена":
                msg_key(uid, "Действие отменено", "list.json")
                mode = state['menu']

            elif request == u"Посмотреть оценки":
                dbx_read(str(uid)+'.txt')
                plin = open(str(uid)+'.txt', 'r')
                fid = int(plin.readline())
                tx = 'Твои оценки:\n'
                for line in plin:
                    txt = line.split(";")
                    if txt[1] == "":
                        tx += txt[0] + ": оценок нет\n"
                    else:
                        tx += txt[0] + ": " + txt[1] + " (средняя: " + "%.2f" % (sum([int(i) for i in txt[1]])*1.0/len(txt[1])) + ")\n"

                if tx == 'Твои оценки:\n': tx = 'У тебя пока ничего нет'
                msg_key(uid, tx, "list.json")
                plin.close()

            elif request == u"Удалить оценку":
                dbx_read(str(uid)+'.txt')
                plin = open(str(uid)+'.txt', 'r')
                fid = int(plin.readline())
                tx = ("Введи номер предмета, который тебе нужен, далее напиши порядковый номер оценки, " +
                "начиная с нуля (отрицательные значения позволяют считать с конца, т.е. -1 -последняя)" +
                "(например, 1 2)\n")
                mode = state['sub_mark']
                num = 1
                for line in plin:
                    txt = line.split(";")
                    #print(line)
                    tx += str(num) + ". " + txt[0] + ": " + txt[1] + "\n"
                    num+=1
                plin.close()
                if tx[-4:-1] == " 2)\n":
                    msg_key(uid, "У тебя пока нет предметов", "list.json")
                    mode = state['menu']
                else:
                    msg_key(uid, tx, "cancel.json")
                    nums_subj = num-1

            elif mode == state['sub_mark'] and request != u"Отмена":
                if len(request.split())==2:
                    num, mrk = [int(i) for i in request.split()]

                    if num > nums_subj or num < 1:
                        msg_key(uid, "Выбран неверный номер. Попробуй ещё раз", "cancel.json")

                    else:
                        try:
                            marks = read(str(uid)+'.txt', 1, num)
                            mark = marks[mrk]

                        except IndexError:
                            msg_key(uid, "Введён неверный номер оценки. Попробуй ещё раз", "cancel.json")
                        else:
                            lm = [i for i in marks]
                            del lm[mrk]
                            replace(str(uid)+'.txt', 1, num, ''.join(lm))
                            dbx_upload(str(uid)+'.txt')
                            msg_key(uid, "Данные успешно сохранены!", "list.json")
                            mode = state['menu']
                else:
                    msg_key(uid, "Данные введены неверно. Попробуй ещё раз", "cancel.json")

            elif request == u"Удалить все оценки":
                msg_key(uid, "Вы уверены, что хотите удалить все оценки из дневника? Предметы и степени злости сохранятся", "del_all.json")

            elif request == u"Да, удалить всё":
                if mode != state['del']:
                    dbx_read(str(uid)+'.txt')
                    plin = open(str(uid)+'.txt', 'r')
                    fid = int(plin.readline())
                    num = 1
                    for line in plin:
                        replace(str(uid)+'.txt', 1, num, "")
                        num+=1
                else:
                    plin = open(str(uid)+'.txt', 'w')
                    plin.write(str(uid))
                    plin.close()
                dbx_upload(str(uid)+'.txt')
                mode = state['menu']
                msg_key(uid, "Дневник очищен!", "list.json")

            elif request == u"Удалить всё":
                mode = state['del']
                msg_key(uid, "Вы уверены, что хотите удалить абсолютно всё из дневника?", "del_all.json")


            elif request == u"Удалить предмет":
                dbx_read(str(uid)+'.txt')
                plin = open(str(uid)+'.txt', 'r')
                fid = int(plin.readline())
                tx = ("Введи номер предмета, который нужно удалить\n")
                mode = state['del_subj']
                num = 1
                for line in plin:
                    txt = line.split(";")
                    #print(line)
                    tx += str(num) + ". " + txt[0] + "\n"
                    num+=1
                plin.close()
                if tx[-4:-1] == "ить\n":
                    msg_key(uid, "У тебя пока нет предметов", "list.json")
                    mode = state['menu']
                else:
                    msg_key(uid, tx, "cancel.json")
                    nums_subj = num-1


            elif mode == state['del_subj'] and request != u"Отмена":
                num = int(request)

                if num > nums_subj or num < 1:
                    msg_key(uid, "Выбран неверный номер. Попробуй ещё раз", "cancel.json")

                else:
                    delete(str(uid)+'.txt', num)
                    dbx_upload(str(uid)+'.txt')
                    msg_key(uid, "Предмет удалён!", "list.json")
                    mode = state['menu']

            elif request == u"Добавить оценки":
                dbx_read(str(uid)+'.txt')
                plin = open(str(uid)+'.txt', 'r')
                fid = int(plin.readline())
                tx = 'Введи номер предмета, который тебе нужен, далее напиши новые оценки (например, 1 54)\n'
                mode = state['add_mark']
                num = 1
                for line in plin:
                    txt = line.split(";")
                    if txt[1] == "":
                        tx += str(num) + ". " + txt[0] + ": оценок нет\n"
                    else:
                        tx += str(num) + ". " + txt[0] + ": " + txt[1] + "\n"
                    num+=1
                plin.close()
                if tx == 'Введи номер предмета, который тебе нужен, далее напиши новые оценки (например, 1 54)\n':
                    msg_key(uid, "У тебя пока нет предметов", "list.json")
                    mode = state['menu']
                else:
                    msg_key(uid, tx, "cancel.json")
                    nums_subj = num-1

            elif mode == state['add_mark'] and request != u"Отмена":
                if len(request.split())==2:
                    num, mrk = [int(i) for i in request.split()]

                    if num > nums_subj or num < 1:
                        msg_key(uid, "Выбран неверный номер. Попробуй ещё раз", "cancel.json")

                    else:
                        for i in str(mrk):
                            print(i)
                            if int(i)<1 or int(i)>5:
                                msg_key(uid, "Введены некорректные оценки. Попробуй ещё раз", "cancel.json")
                                break
                        else:
                            #plin = open(str(uid)+'.txt', 'r')
                            marks = read(str(uid)+'.txt', 1, num)
                            replace(str(uid)+'.txt', 1, num, marks+str(mrk))
                            dbx_upload(str(uid)+'.txt')
                            msg_key(uid, "Данные успешно сохранены!", "list.json")
                            mode = state['menu']
                else:
                    msg_key(uid, "Данные введены неверно. Попробуй ещё раз", "cancel.json")

            elif request == u"Изменить степень злости учителя":
                msg_key(uid, "Степень злости учителя нельзя изменить :)", "list.json")

            elif request == u"Посчитать оценки":
                dbx_read(str(uid)+'.txt')
                plin = open(str(uid)+'.txt', 'r')
                fid = int(plin.readline())
                tx = 'Введи номер предмета, который тебе нужен:\n'
                num = 1
                mode = state['calc']
                for line in plin:
                    txt = line.split(";")
                    if txt[1] == "":
                        tx += str(num) + ". " + txt[0] + ": оценок нет\n"
                    else:
                        tx += str(num) + ". " + txt[0] + " (средняя: " + "%.2f" % (sum([int(i) for i in txt[1]])*1.0/len(txt[1])) + ")\n"
                    num += 1

                plin.close()
                if tx == 'Введи номер предмета, который тебе нужен:\n':
                    msg_key(uid, "У тебя пока ничего нет", "list.json")
                else:
                    msg_key(uid, tx, "cancel.json")
                    nums_subj = num-1

            elif mode == state['calc'] and request != u"Отмена":
                sel = int(request)
                if sel > nums_subj or sel < 1:
                    msg_key(uid, "Выбран неверный номер. Попробуй ещё раз", "cancel.json")

                else:
                    plin = open(str(uid)+'.txt', 'r')
                    fid = int(plin.readline())
                    num = 1
                    while num<=sel:
                        txt = plin.readline().split(";")
                        num += 1

                    if txt[1] == '':
                        msg_key(uid, "Выбран предмет без оценок. Выбери другой", "cancel.json")
                    else:
                        summ = sum([int(i) for i in txt[1]])
                        k = len(txt[1])
                        okrg = int(txt[2])
                        sr = summ*1.0/k
                        msg(uid, "Средняя оценка: " + "%.2f" % sr)

                        txt = ""
                        for mark in range(ceil(sr), 6):
                            if ceil(sr)==5:
                                msg_key(uid, txt + "Поздравляю, у тебя чистая пятёрка! Продолжай в том же духе!", "list.json")
                                break
                            txt += "Чтобы получить " + mark_d[mark] + ", нужно заработать "
                            for cm in range(mark, 6):
                                if cm > mark: txt += ", либо "
                                count = calc_mark(summ, k, mark, okrg, cm)
                                txt += str(count)
                                txt += str(name_marks[cm-2][word(count)])
                            txt += "\n"
                        else:
                            msg_key(uid, txt + "\nУдачи!", "list.json")

            else: msg_key(event.user_id, "Прости, но я не понимаю тебя", "key.json")
