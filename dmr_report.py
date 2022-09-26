# Copyright (c) 2013, Radhika and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from datetime import timedelta
from warnings import filters

def execute(filters=None):
	columns = get_columns()
	data=get_data(filters=filters)
	return columns, data

def get_columns():
	columns=[
		{"label": ("Date"), "fieldname": "date", "fieldtype": "Data", "width": 100},
		{"label": ("Total Enquiry"), "fieldname": "total_enquiry", "fieldtype": "Data", "width": 100},
		{"label": ("Total Quotations"), "fieldname": "total_quotations", "fieldtype": "Int", "width": 150},
		{"label": ("Today Quotations"), "fieldname": "today_quotations", "fieldtype": "Int", "width": 150},
		{"label": ("Old Quotations"), "fieldname": "old_quotations", "fieldtype": "Int", "width": 150},
		{"label": ("Pending Quotations"), "fieldname": "pending_quotations", "fieldtype": "Int", "width": 150},
		{"label": ("Order Booked"), "fieldname": "order_booked", "fieldtype": "Int", "width": 150},
		{"label": ("Order Lost"), "fieldname": "order_lost", "fieldtype": "Int", "width": 150},
		{"label": ("Followup Open Balance"), "fieldname": "followup_ob", "fieldtype": "Int", "width": 150},
		{"label": ("Followup Booked"), "fieldname": "followup_booked", "fieldtype": "Int", "width": 150},
		{"label": ("Followup Lost"), "fieldname": "followup_lost", "fieldtype": "Int", "width": 150},
		{"label": ("Followup Closing Balance"), "fieldname": "followup_cb", "fieldtype": "Int", "width": 150},
		{"label": ("Order Booked"), "fieldname": "order_booked_so", "fieldtype": "Amount", "width": 150}
	]
	return columns

def get_data(filters=filters):
	if filters['from_date'] < filters['to_date']:
		data=[]
		total_no_of_days,BeginDate,EndDate=fetch_no_of_days(filters=filters)
		x=0

		total_enquiry_count = 0
		total_quotations_count = 0
		old_quotations_count = 0
		today_quotations_count = 0
		pending_quotations_count = 0
		order_booked_count = 0
		order_lost_count = 0
		followup_ob_count = 0
		followup_booked_count = 0
		followup_lost_count = 0
		followup_cb_count = 0
		value_of_orders_count = 0

		while x <= int(total_no_of_days.days):
			if x==0:
				next_date=BeginDate
			else:
				next_date=next_date
				
			Dict=append_data_vales(next_date)
			data.append(Dict)

			total_enquiry_count += Dict['total_enquiry']
			total_quotations_count += Dict['total_quotations']
			old_quotations_count += Dict['old_quotations']
			today_quotations_count += Dict['today_quotations']
			pending_quotations_count += Dict['pending_quotations']
			order_booked_count += Dict['order_booked']
			order_lost_count += Dict['order_lost']
			followup_ob_count += Dict['followup_ob']
			followup_booked_count += Dict['followup_booked']
			followup_lost_count += Dict['followup_lost']
			followup_cb_count += Dict['followup_cb']
			value_of_orders_count += Dict['order_booked_so']
			x+=1
			next_date=next_date+ timedelta(days=1)
		TotalDict = {'date':'Total', 'total_enquiry':total_enquiry_count,'total_quotations':total_quotations_count,'old_quotations':old_quotations_count,'today_quotations':today_quotations_count, 'pending_quotations':pending_quotations_count,'order_booked':order_booked_count,'order_lost':order_lost_count, 'followup_ob':followup_ob_count, 'followup_booked':followup_booked_count, 'followup_lost':followup_lost_count, 'followup_cb':followup_cb_count, 'order_booked_so':round(value_of_orders_count,2)}
		# data.append(empty_row_dict)
		print(filters['to_date'])
		ob_opp=frappe.db.sql("""select name from `tabOpportunity` where transaction_date < %(next_date)s and status = 'Quotation'""",{'next_date': filters['to_date']},as_dict=1)
		print(ob_opp)
		if (TotalDict['total_enquiry'] == 0):
			cp_quo_today, cp_quo_old = 0, 0
		else:
			cp_quo_today = (TotalDict['today_quotations']/TotalDict['total_enquiry'])*100
			cp_quo_old = (TotalDict['old_quotations']/TotalDict['total_enquiry'])*100
		if (TotalDict['today_quotations']) == 0:
			cp_order_booked, cp_order_lost = 0, 0
		else:
			cp_order_booked = (TotalDict['order_booked']/TotalDict['today_quotations'])*100
			cp_order_lost = (TotalDict['order_lost']/TotalDict['today_quotations'])*100
		if(len(ob_opp) == 0):
			cp_followup_booked, cp_followup_lost = 0, 0
		else:
			cp_followup_booked = (TotalDict['followup_booked']/len(ob_opp))*100
			cp_followup_lost = (TotalDict['followup_lost']/len(ob_opp))*100

		data.append(TotalDict)

		cp_Dict = {'date':'Conversion Percentage', 'today_quotations':cp_quo_today,'old_quotations':cp_quo_old ,'order_booked':cp_order_booked,'order_lost':cp_order_lost, 'followup_booked':cp_followup_booked, 'followup_lost':cp_followup_lost}
		# data.append(empty_row_dict)
		data.append(cp_Dict)

		return data
	else:
		frappe.msgprint("Please select valid date")

def fetch_no_of_days(filters=filters):
	BeginDate=datetime.strptime(filters['from_date'], "%Y-%m-%d")
	EndDate=datetime.strptime(filters['to_date'], "%Y-%m-%d")
	total_no_of_days=EndDate-BeginDate
	return total_no_of_days,BeginDate,EndDate

def append_data_vales(next_date):
	opportunity_records=frappe.db.sql("""select name from `tabOpportunity` where transaction_date = %(next_date)s""",{'next_date': next_date},as_dict=1)
	quo_records=frappe.db.sql("""select name from `tabQuotation` where transaction_date = %(next_date)s""",{'next_date': next_date},as_dict=1)
	today_quo = frappe.db.sql("""select name from `tabQuotation` where transaction_date = %(next_date)s and opportunity in (select name from `tabOpportunity` where transaction_date = %(next_date)s)""",{'next_date': next_date},as_dict=1)
	old_quo = frappe.db.sql("""select name from `tabQuotation` where transaction_date = %(next_date)s and opportunity in (select name from `tabOpportunity` where transaction_date < %(next_date)s)""", {'next_date': next_date},as_dict=1)
	pending_quo = frappe.db.sql("""select name from `tabOpportunity` where transaction_date = %(next_date)s and status = 'Draft'""",{'next_date': next_date},as_dict=1)
	quo_order_booked = frappe.db.sql("""select name from `tabQuotation` where transaction_date = %(next_date)s and status = 'Ordered'""",{'next_date': next_date},as_dict=1)
	quo_lost_records=frappe.db.sql("""Select name from `tabQuotation` where transaction_date = %(next_date)s and status = 'Lost'""",{'next_date': next_date},as_dict=1)
	followup_ob_old_opp=frappe.db.sql("""select name from `tabOpportunity` where transaction_date < %(next_date)s and status = 'Quotation'""",{'next_date': next_date},as_dict=1)
	old_quo_booked = frappe.db.sql("""select name from `tabQuotation` where transaction_date < %(next_date)s and status='Ordered'""", {'next_date': next_date},as_dict=1)
	old_quo_lost_records=frappe.db.sql("""select name from `tabQuotation` where transaction_date < %(next_date)s and status = 'Lost'""",{'next_date': next_date},as_dict=1)
	value_of_orders = frappe.db.sql("""select sum(total) as total from `tabSales Order` where transaction_date = %(next_date)s """,{'next_date': next_date},as_dict=1)

	closing_bal = len(followup_ob_old_opp) - len(old_quo_booked) - len(old_quo_lost_records)

	if next_date:
		date=next_date.strftime("%d/%m/%Y")
	if value_of_orders[0]['total'] == None:
		value_of_orders1 = 0
	else:
		value_of_orders1 = value_of_orders[0]['total']
	print(round(value_of_orders1, 2))
	Dict = {'date':date,'total_enquiry': len(opportunity_records), 'total_quotations':len(quo_records),'old_quotations':len(old_quo),'today_quotations':len(today_quo), 'pending_quotations':len(pending_quo),'order_booked':len(quo_order_booked),'order_lost':len(quo_lost_records), 'followup_ob':len(followup_ob_old_opp), 'followup_booked':len(old_quo_booked), 'followup_lost':len(old_quo_lost_records), 'followup_cb':closing_bal, 'order_booked_so':round(value_of_orders1, 2)}
	return Dict