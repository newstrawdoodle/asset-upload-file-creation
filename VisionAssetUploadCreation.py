#Things you need to do before running the script, run the following commands to download additional libraries
#py -m pip install pandas
#py -m pip install openpyxl

#Initial version of the file will copy a specified file name in the script location and save the file into that same location. this can then be copied over to the desired Asset upload location.
#Pandas library is used to make copying columns and modifying columns easy.
#Read up on Tkinter for a more friendly UI input instead of through commandline
##################################################################################
#Things to add
#File name creation to follow naming convention of Meter Manufacturer-Customer-PO #-Batch #-meter count
#Files read from variable location based on Customer
#Files saved to variable location based on Customer
################################################################################


import os
import datetime as dt
import pandas as pd

def getTimeSetting():
    """ This function makes sure the user inputs only true or false, it will loop until one of those is entered. """
    timeSetting = input('Is the Meter Time Setting Verified? True or False?').upper()
    if timeSetting == 'TRUE':
        newValue = True
    elif timeSetting == 'FALSE':
        newValue = False
    else:
        print("Incorrect input. Please enter 'True' or 'False'." )
        newValue =  getTimeSetting()
    return newValue

def getCustomer():
    """This list needs to be updated whenever new customers get added so that the file can validate against those new names. """
    cust =input('Enter Customer: ').upper()
    custList = [
        'AVAMO', 'PIEG', 'FLORA', 'MADISON', 'METRO', 'OATI', 'SMU'
        ]
    if cust in custList:
        realCust = cust
    else:
        realCust = getCustomer()
    return realCust
def getMeterConfigType():
    """This function makes suere the user inputs only Commercial or Residential for the meterConfigType. It will loop until this is met. """
    meterConfig = input('Are these meters Commercial or Residential? ').capitalize()
    if meterConfig == 'Commercial':
        configType = 'Commercial'
    elif meterConfig == 'Residential':
        configType = 'Residential'
    else:
        print("Incorrect input. Please enter 'Commercial' or 'Residential'." )
        configType =  getMeterConfigType()
    return configType
    
    
def main():
    """Calls helper functions to collects various inputs from the user. 
    This will also convert the user input to the correct case sensitivity. 
    It will also validate the input from the user to make sure the user is not putting in "junk" data."""
    customer= getCustomer()
    meterConfigType= getMeterConfigType()
    timeSetting = getTimeSetting()
    #Check User inputted values to make sure they are an expected values
    #I need to check the timeSetting input to make sure the user input either True or False.
    #I might want to add some data validation for the other user inputs as well.
    #Set Script & File Paths
    fileName='PresqueIsle_PT223081-PO-RMA 15325-Swap_20240313.xlsx'
    scriptPath = os.path.dirname(__file__)
    scriptPathMMF = fr'\\devfs\e2e\Docs\AMIot\Asset_Upload\Asset_Files\{customer}\MMF\Lora Electric Meters\Pending files'
    scriptPathUpload = fr'\\devfs\e2e\Docs\AMIot\Asset_Upload\Asset_Files\{customer}\Upload\Electric'
    filePath1 = os.path.join(scriptPath,fileName)

    #Open all existing files (not the output)
    file1 = pd.read_excel(filePath1)
    #Set index on the tables to the "Manufacturer_SN" column
    file1.set_index('Meter_Manufacturer',inplace=True)
    #Grab final file name variables
    fileManufacture = file1.index[0]
    fileCustomer = customer
    filePONumber = file1.iat[0,1]
    fileBatch = str(file1.iat[0,2])
    meterCount = str(len(file1))
    print(fileManufacture)
    print(fileCustomer)
    print(filePONumber)
    print(fileBatch)
    print(f'The DataFrame has {meterCount} rows.')
    #newFileName = fileManufacture+'_'fileCustomer+'_',filePONumber+'_',fileBatch+'.csv'
    newFileName = fileManufacture+'_'+fileCustomer+'_'+filePONumber+'_'+fileBatch+'_'+'Meters '+meterCount+'.csv'
    #newFileName = str(newFileName)
    
    newFilePath = os.path.join(scriptPath,newFileName)
    #Add Static info to specific columns
    file1['Meter_Model_Revision']='1.0.0.0'
    file1['MeterConfigurationType']=meterConfigType
    file1['MeterCommissionStatus']='Customer Inventory'
    file1['MeterCommissionStatusDetail']='Customer Inventory'
    file1['Meter_TimeSetting_Verified']= timeSetting 
    file1['Modem_Manufacturer']=file1.index
    file1['Modem_Model_Revision']='1.0.0.0'
    file1['ModemConfigurationType']=file1['MeterConfigurationType']
    file1['ModemCommissionStatus']='Customer Inventory'
    file1['ModemCommissionStatusDetail']='Customer Inventory'
    file1['Meter_ServiceType']='ELECTRICITY_METER'
    file1['Modem_ServiceType']='LORAWAN_MODEM'
    file1['Customer_Name']=customer
    file1['AssetLotNumber']='0'
    file1['AssetPurchasePrice']='0'
    file1['ModemDeviceType']=''
    file1['Meter_Form']=file1['Manufacturer_Type']
    
    #Replace Meter_TimeSetting with the correct value
    file1['Meter_TimeSetting'].replace(
        {
            'Eastern' : 'America/New_York',
            'Central' : 'America/Chicago',
            'Mountain' : 'America/Denver'
        },
        inplace=True
    )
    
    #rename columns to match desired upload name
    file1['Meter_ID']=file1['Manufacturer_SN']
    file1['AssetPallet']=file1['Pallet']
    file1['AssetBox']=file1['Box']
    file1['AssetBatch']=file1['Batch']
    
    
    #changing date and time to Epoch time in milliseconds
    file1['ShipmentDate'] = (pd.to_datetime(file1['Ship_Date']) - dt.datetime(1970,1,1)).dt.total_seconds()*1000
    file1['ShipmentDateConverted'] = pd.to_datetime(file1['ShipmentDate']/1000, unit='s')
    
    #Convert the Meter FW and Modem_FW Columns to all Caps
    file1['Meter_FW'] = file1['Meter_FW'].str.upper()
    file1['Modem_FW'] = file1['Modem_FW'].str.upper()
    
    #Joins information to create the Meter Firmware file
    file1['Meter_FW']= customer+'-'+file1['Meter_FW']+'-'+file1['Modem_FW']

    #Reorder columns    
    cols = ['Meter_ID','Manufacturer_SN','Meter_Model','Meter_Model_Revision','Meter_FW','Meter_Form','Meter_Class','MeterConfigurationType','MeterCommissionStatus','MeterCommissionStatusDetail','Meter_TimeSetting','Meter_TimeSetting_Verified','Modem_Manufacturer','Modem_ID','Modem_SN','Modem_Model','Modem_Model_Revision','Modem_FW','ModemConfigurationType','LoRa_DevEUI','LoRa_JoinEUI','LoRa_AppKey','LoRa_NetworkKey','ModemCommissionStatus','ModemCommissionStatusDetail','ModemDeviceType','Meter_ServiceType','Modem_ServiceType','PO_Number','AssetPallet','AssetLotNumber','AssetPurchasePrice','ShipmentDate','AssetBatch','AssetBox']
    file1 = file1[cols]

    #Export as a new file
    file1.to_csv(newFilePath)



    return

if __name__ == '__main__':
    main()
