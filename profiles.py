class Entity:

    def __init__(self, name, rg=None, cpf=None, cnpj=None):
        self.name = name
        self.rg = rg
        self.cpf = cpf
        self.cnpj = cnpj

    @property
    def cpf(self):
        return self._cpf

    @cpf.setter
    def cpf(self, cpf_number):
        if cpf_number and len(cpf_number) == 11:
            self._cpf = cpf_number
        else:
            self._cpf = None
    
    @property
    def cnpj(self):
        return self._cnpj

    @cnpj.setter
    def cnpj(self, cnpj_number):
        if cnpj_number and len(cnpj_number) == 14:
            self._cnpj = cnpj_number
        else:
            self._cnpj = None

    def get_formated_cpf(self):
        if self.cpf:
            return f"{self.cpf[:3]}.{self.cpf[3:6]}.{self.cpf[6:9]}-{self.cpf[9:]}"

    def get_formated_cnpj(self):
        if self.cnpj:
            return f"{self.cnpj[:2]}.{self.cnpj[2:5]}.{self.cnpj[5:8]}/{self.cnpj[8:12]}-{self.cnpj[12:]}"
    

class Client:

    def __init__(self, name, store_name, rg, cpf, cnpj, street, number, neighborhood, city, state, country, cep, email):
        self.client = Entity(name=name, rg=rg, cpf=cpf)
        self.store = Entity(name=store_name, cnpj=cnpj)
        self.street = street
        self.number = number
        self.neighborhood = neighborhood
        self.city = city
        self.state = state
        self.country = country
        self.cep = cep
        self.email = email

    @property
    def address(self):
        return f"{self.street}, {self.number} - {self.neighborhood}, {self.city}, {self.state}"


class EJ:

    def __init__(self, ata_date, president, president_rg, president_cpf, gi, gi_rg, gi_cpf):
        self.ata_date = ata_date
        self.president = Entity(name=president, rg=president_rg, cpf=president_cpf)
        self.gi = Entity(name=gi, rg=gi_rg, cpf=gi_cpf)


class Service:
    
    def __init__(self, type_contract, deadline, short_service_description, price, payment, payment_price, service_list):
        self.type_contract = type_contract 
        self.deadline = deadline 
        self.short_service_description = short_service_description 
        self.price = price
        self.payment = payment
        self.payment_price = payment_price 
        self.service_list = service_list
