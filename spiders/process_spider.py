# -*- coding: utf-8 -*-
import scrapy
import urllib.parse



class ProcessSpider(scrapy.Spider):
    name = "Process"
    form = {}
    url = 'https://consultaprocesos.ramajudicial.gov.co/Procesos/NumeroRadicacion'

    def start_requests(self):
        """ First request to URL to get headers and start scraping"""
        yield scrapy.Request(self.url, callback=self.input_process, method='GET')

    def input_process(self, response):
        """ Get credentials of a process id """

        for i, form_data in enumerate(response.xpath("//form[@id='Consulta']//input"), start=1):
            name = form_data.xpath(f"//input[{i}]/@name").get()
            value = form_data.xpath(f"//input[{i}]/@value").get()
            if name:
                ProcessSpider.form[name] = str(value)

        ProcessSpider.form['NumeroRadicacion'] = self.process_id

        args = urllib.parse.urlencode(ProcessSpider.form)

        yield scrapy.FormRequest(f"{self.url}?{args}",
                                 callback=self.get_details,
                                 method='POST',
                                 headers=response.headers)

    def get_details(self, response):
        """ Get details of the process information """
        id_process = response.xpath("//a[@onclick='PostIdProceso(event)']/@id").get()

        ProcessSpider.form['IdProceso'] = id_process

        args = urllib.parse.urlencode(ProcessSpider.form)

        yield scrapy.FormRequest(f"{self.url}?{args}",
                                 callback=self.parse_details,
                                 method='POST',
                                 headers=response.headers,
                                 encoding='utf-8')

    def parse_details(self, response):
        """ Parse the details of the process """

        """ General Data of the process"""

        radicated_at = response.xpath("normalize-space(//div[@id='FechaProceso']/text())").get()
        TipoProceso = response.xpath("normalize-space(//div[@id='TipoProceso']/text())").get()

        """ Parties """

        parties_table = response.xpath("//div[@class='container table-responsive' "
                                       "and .//span[text()='Sujetos Procesales']]")

        party_types = parties_table.xpath('.//thead/tr/th/text()').getall()
        parties_data = parties_table.xpath('.//tbody/tr/td/text()').getall()

        parties, i = [], 0

        while i < len(parties_data):
            dic = {}
            for j in range(len(party_types)):
                dic[party_types[j]] = parties_data[i]
                if j < len(party_types) - 1:
                    i += 1
            i += 1
            parties.append(dic)

        """ Judge Information """

        name_despacho = response.xpath("normalize-space(//div[@id='Despacho']/text())").get()
        judge = response.xpath("normalize-space(//div[@id='Ponente']/text())").get()
        county = name_despacho.split()[-1]

        """ Movements """

        dic_actua = []
        movements_table = response.xpath("//div[@class='container table-responsive' "
                                         "and .//span[text()='Actuaciones del Proceso']]")

        actua_types = []

        for types in movements_table.xpath('.//thead/tr/th'):
            t = types.xpath('normalize-space(./text())').get()
            actua_types.append(t)

        actua_data = []

        for movement in movements_table.xpath('.//tbody/tr/td'):
            m = movement.xpath('normalize-space(./text())').get()
            actua_data.append(m)

        print(actua_types)
        print(actua_data)

        movements, i = [], 0

        while i < len(actua_data):
            dic = {}
            for j in range(len(actua_types)):
                if j < len(actua_types) - 1:
                    dic[actua_types[j]] = actua_data[i]
                    i += 1
            i += 1
            movements.append(dic)

        print(movements)


        data = {
            'radicated_at': radicated_at,
            'type_proc': TipoProceso,
            'parties': parties,
            'office': {
                'name': name_despacho,
                'judge': judge,
                'city': county
            },
            'movements': actua_data,
            'location': county
        }



        self.outputResponse['result'] = data
