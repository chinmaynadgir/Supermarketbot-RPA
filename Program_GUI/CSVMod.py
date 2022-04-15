# importing the csv module
import csv

#initializing everything to hundred
def initialize_items() :
	inventory_dict=[
	{'item':'sanitizer_l','quantity':'100'},
	{'item':'mask_l','quantity':'100'},
	{'item':'hand_gloves_l','quantity':'100'},
	{'item':'syrup_l','quantity':'100'},
	{'item':'cream_l','quantity':'100'},
	{'item':'thermal_gun_l','quantity':'100'},
	{'item':'rice_l','quantity':'100'},
	{'item':'food_oil_l','quantity':'100'},
	{'item':'wheat_l','quantity':'100'},
	{'item':'spices_l','quantity':'100'},
	{'item':'flour_l','quantity':'100'},
	{'item':'maggi_l','quantity':'100'},
	{'item':'sprite_l','quantity':'100'},
	{'item':'mineral_l','quantity':'100'},
	{'item':'juice_l','quantity':'100'},
	{'item':'coke_l','quantity':'100'},
	{'item':'lassi_l','quantity':'100'},
	{'item':'mountain_duo_l','quantity':'100'},
	]
	
	# field names
	fields = ['item', 'quantity']

	# name of csv file
	filename = "inventory_records1.csv"

	# writing to csv file
	with open(filename, 'w',encoding='UTF8',newline='') as csvfile:
		# creating a csv dict writer object
		writer = csv.DictWriter(csvfile, fieldnames = fields,delimiter=",")
		
		
		# writing headers (field names)
		writer.writeheader()
		
		# writing data rows
		writer.writerows(inventory_dict)

	csvfile.close()
	
initialize_items()