from glob import glob
import csv


unformatted_logs = glob('ampl_logs/*.log') 

for file in unformatted_logs:
	# specify input and output file
	file_num =  file[-8:-4]
	f = open(file)

	with open('ampl_logs/ampl_log'+ file_num +' .csv', 'wb') as out:
		writer = csv.writer(out)
		
		#write header
		header = 'DateNo Obj-Function   sw_term wf_term orop_term tg_offset  oprc overage penalty'
		header = header.split()
		writer.writerow(header)

		for _ in range(1336):
			next(f)
		for line in f:
			if line[0] != 'D' and line[0] != 'T' and len(line) > 1:
				formatted_line = line.split()
				if len(formatted_line[3]) > 4:
					if len(formatted_line[2])> 12:
						obj = formatted_line[2][:12]
						sw = formatted_line[2][12:]
						wf_term = formatted_line[3][0:3]
						orop_term = formatted_line[3][4:]
						new_list = [formatted_line[0], obj, sw, \
						 wf_term, orop_term, formatted_line[4], \
						  formatted_line[5], formatted_line[6]]
					else:
						wf_term = formatted_line[3][0:3]
						orop_term = formatted_line[3][4:]
						new_list = [formatted_line[0], formatted_line[1],\
						 formatted_line[2], wf_term, orop_term, \
						 formatted_line[4], formatted_line[5], \
						 formatted_line[6], formatted_line[7]]
					writer.writerow(new_list)
				elif len(formatted_line[2])> 12:
					obj = formatted_line[2][:12]
					sw = formatted_line[2][12:]
					wf_term = formatted_line[3][0:3]
					orop_term = formatted_line[3][4:]
					new_list = [formatted_line[0], obj, sw, \
					 formatted_line[3], formatted_line[4], \
					  formatted_line[5], formatted_line[6], \
					 formatted_line[7]]
					writer.writerow(new_list)
				else:
					writer.writerow(formatted_line)
	f.close()