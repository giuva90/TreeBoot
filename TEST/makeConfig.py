import configparser

conf = configparser.ConfigParser()
conf.add_section('ZOO')
conf.set('ZOO', 'data_column', '1,2,3,6')

with open('example.ini', 'w') as configfile:
	conf.write(configfile)
