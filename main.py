from collections import UserDict
from datetime import datetime
import pickle


class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
            self.__value = value

class Name(Field):
    pass

class Phone(Field):
    @Field.value.setter
    def value(self, value):
        if not value.isnumeric():
            raise ValueError('Wrong phone! Please, enter only digital.')
        if len(value) == 10:
            pass
        elif len(value) == 12:
            if value[0] != 0:
                raise ValueError('Wrong phone! The operator kod has to start from zero.')
        else:
            # if len(value) != 12:
            raise ValueError('Wrong phone! Length of phone must be 10 or 12 digits.')
        self.__value = value

class Birthday(Field):
    @Field.value.setter
    def value(self, value):
        # day, month, year = value.strip().split(' ')
        currentdate = datetime.now().date()
        # value.date()
        # list_month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        # if int(day) < 1  or int(day) > 31:
        #     raise ValueError('Wrong birthday! The day must be in the range from 1 to 31.')
        # if month not in list_month:
        #     raise ValueError('Wrong birthday! The month must be string and true. For example: "May"')
        # if len(year) != 4: 
        #     raise ValueError('Wrong birthday! The year have 4 digital.')
        # if int(year) > currentdate.year:
        #     raise ValueError('Wrong birthday! The year must be in past or current.')
        # if month == "February":
        #     if int(day) <= 1 or int(day) >= 29:
        #         raise ValueError('Wrong birthday! The February have days from 1 to 29.')
        if value > currentdate:
            raise ValueError("Wrong birthday! The date must be in past or current")
        self.__value = value

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def delete_phone(self, phone):
        for number in self.phones:
            if number.value == phone:
                self.phones.remove(number)
                return True
        return False

    def change_phone(self, old_phone, new_phone):
        for number in self.phones:
            if number.value == old_phone:
                self.delete_phone(old_phone)
                self.add_phone(new_phone)
        return self.phones
    
    def search_data(self):
        user_phones = []
        birth_info = ''
        for phone in self.phones:
            user_phones.append(phone.value)
        
        if self.birthday:
            birth_info = f'(Birthday: {self.birthday.value})'

        return f'{self.name.value} : {user_phones}{birth_info}'
    
    """Додає день народження та розраховує залишок днів до його настання"""  
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
    
    def days_to_birthday(self):
        current_datetime = datetime.now()
        date_birthday = datetime.strptime(self.birthday.value, '%d %B %Y')
        if date_birthday.month > current_datetime.month:
            birth_date = datetime(year=current_datetime.year, month=date_birthday.month, day=date_birthday.day)
            time_left = birth_date - current_datetime
        elif date_birthday.month < current_datetime.month:
            birth_date = datetime(year=current_datetime.year+1, month=date_birthday.month, day=date_birthday.day)
            time_left = birth_date - current_datetime
        else:
            if date_birthday.day > current_datetime.day:
                time_left = date_birthday.day - current_datetime.day
            elif date_birthday.day < current_datetime.day:
                birth_date = datetime(year=current_datetime.year+1, month=date_birthday.month, day=date_birthday.day)
                time_left = birth_date - current_datetime
            else:
                return f'Happy birthday!'
    
        return f'{time_left} days left to birthday'


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.file_name = 'data.bin'
        self.open_file()

    def add_record(self, record):
        self.data[record.name.value] = record
         
    def get_all_record(self):
        return self.data
    
    # def has_record(self, name):
    #     return bool(self.data.get(name))

    # def get_record(self, name) -> Record:
    #     return self.data.get(name)

    def search(self, value):
        record_result = []
        for record in self.get_all_record().values():
            if value in record.name.value:
                record_result.append(record)
                continue

            for phone in record.phones:
                if value in phone.value:
                    record_result.append(record)

        if not record_result:
            raise ValueError("There are no contacts for your request.")
        return record_result
    
    def remove_record(self, name):
        del self.data[name]
    
    def iterator(self, amount_records=10):
        page = []
        counter = 0
        for record in self.data:
            page.append(self.data[record])
            counter += 1

            if counter == amount_records:
                yield page
                page = []
                counter = 0
        if page:
            yield page
    
    def save_file(self):
        # file_name = 'data.bin'
        with open(self.file_name, "wb") as fh:
            pickle.dump(self.data, fh)

    def open_file(self):
        try:
            with open(self.file_name, "rb") as fh:
                self.data = pickle.load(fh)
        except FileNotFoundError:
            pass


contacts = AddressBook()

"""
Декоратор винятків.
"""
def input_error(func):
    def miss_name(command):
        try:
            res = func(command)
            if res == None:
                return 'Enter user name. The first letter is capital, and the rest are small.'
            return res
        except (KeyError, IndexError):
            return 'Give your name and phone number, please!'   
    return miss_name
    
""" 
Функції обробники команд — handler, що відповідають
за безпосереднє виконання команд. 
"""
def greeting(word):
    return 'How can I help you?'


@input_error
def add_contacts(contact):
    name, phones = create_data(contact)

    if name in contacts:
        raise ValueError('This contact already exist.')
    record = Record(name)

    for phone in phones:
        phone.strip()
        record.add_phone(phone)

    contacts.add_record(record)
    return f'You added new contact: {name} and telephone number {phones}.'

@input_error
def add_birthday(contact):
    try:
        name, birth = create_birth(contact)
    # currentdate = datetime.now()
    # list_month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    # if int(day) < 1  or int(day) > 31:
    #     raise ValueError('Wrong birthday! The day must be in the range from 1 to 31.')
    # if month not in list_month:
    #     raise ValueError('Wrong birthday! The month must be string and true. For example: "May"')
    # if len(year) != 4: 
    #     raise ValueError('Wrong birthday! The year have 4 digital.')
    # if int(year) > currentdate.year:
    #     raise ValueError('Wrong birthday! The year must be in past or current.')
    # if month == "February":
    #     if int(day) <= 1 or int(day) >= 29:
    #         raise ValueError('Wrong birthday! The February have days from 1 to 29.')
        data_birthday = ' '.join(birth)
        birthday = datetime.strptime(data_birthday, '%d %B %Y').date()
        record = contacts[name]
        record.add_birthday(birthday)
        return f'You added to contact {name} birthday {birthday}.'
    except ValueError:
        raise ('Wrong format birthday! Please write in format "birthday <name> <day month year >"/'
                         'For example: birthday Olya 12 June 2002.')

@input_error
def show_wait_birthday(command_string):
    command, name = command_string.split(' ')
    record = contacts[name]
    number = record.days_to_birthday()
    return number

@input_error
def change_contact(number):
    name, phones = create_data(number)
    record = contacts[name]
    record.change_phone(phones)
    return f'You changed contact'

@input_error
def show_contact(command_string):
    search_info = ''
    command, value = command_string.split(' ')
    records = contacts.search(value)
    for record in records:
        search_info += f"{record.search_data()}\n"
    return search_info


def show_all(list_new):
    list_contacts = ''
    for key, record in contacts.get_all_record().items():
        list_contacts += f'{record.search_data()}\n'
    
    return list_contacts

@input_error
def del_func(command_string):
    command, name = command_string.strip().split(' ')
    contacts.remove_record(name)
    return "You deleted the contact."


@input_error
def del_phone(data):
    command_fist, command_second, name, phone = data.strip().split(' ')
    record = contacts[name]
    if record.delete_phone(phone):
        return f'Phone {phone} for {name} contact deleted.'
    return f'{name} contact does not have this number'

def finish(end):
    exit()  

dict_command = {'hello': greeting,
    'add': add_contacts,
    'birthday': add_birthday,
    'change': change_contact,
    'delete phone': del_phone,
    'delete': del_func,
    'phone': show_contact,
    "wait": show_wait_birthday,
    'show all': show_all,
    'good bye': finish,
    'close': finish,
    'exit': finish
}

def create_data(data):
    """
    Розділяє вхідні дані на дві частини - номер і телефон.
    Також ці данні проходять валідацію.
    Для подальшої роботи з ними.
    :param data: Строка з номером і ім'ям.
    :return: Вже розділені ім'я і номер
    """
    command, name, *phones = data.strip().split(' ')

    if name.isnumeric() or name == '':
        raise ValueError('Wrong name. The name is number or you enter two space')
    for phone in phones:
        if not phone.isnumeric():
            raise ValueError('Wrong phones.')
    return name, phones
    
def create_birth(birthdata):
    """
    Розділяє вхідні дані на частини - команда, номер і день народження.
    """
    command, name, *birth = birthdata.strip().split(' ')
    return name, birth

"""
Парсер команд.
Частина, яка відповідає за розбір введених користувачем рядків, 
виділення з рядка ключових слів та модифікаторів команд.
"""
def parser_command(command: str)->str:
    new_command = command.casefold()
    for key, action in dict_command.items():
        if new_command.find(key) >= 0:
            return action(command)
    return 'You input wrong command! Please, try again'

"""
Цикл запит-відповідь. Ця частина програми відповідає за отримання від користувача даних та 
повернення користувачеві відповіді від функції-handlerа.
"""
def main():
    try:
        while True:
            action = input("Please, input your command...") 
            if action == 'exit' or action == 'good bye' or action == 'close':
                print ('Good bye!')
            result = parser_command(action)
            print(result)
    finally:
        contacts.save_file()

if __name__ == '__main__':
    main()