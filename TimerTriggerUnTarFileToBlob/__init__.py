import datetime
import logging
import tarfile
import azure.functions as func
import urllib.request
from azure.storage.blob import BlobServiceClient


def main(mytimer: func.TimerRequest) -> None:
    try:
        utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
        if mytimer.past_due:
            logging.info('The timer is past due!')
        logging.info('Start untaring to Azure Blob Storage....%s', datetime.datetime.utcnow())
        #sourcePath : tar File path or location, TO DO: call from config or lockbox file path?
        sourcePath = 'https://untarblobfunction.blob.core.windows.net/temp/'
        #tarFileName: TO DO: get file from lockbox or read from above path 
        tarFileName = 'pics-3.8.0.tar.gz'
        #fullFilePath: Path of file location
        fullFilePath = sourcePath + tarFileName
        #connectionString: Define Connection to connect to azure account TO DO get from config
        connectionString = "DefaultEndpointsProtocol=https;AccountName=untarblobfunction;AccountKey=ipgr6LlqX1CPNefbUC8foMqRFeYcoqbtdLjEEKAqC2RILhCvbvmT/8qCcs9u/VVyo0pjqGTzKV3XSygfd8lbQQ==;EndpointSuffix=core.windows.net"
        #containerName: Define container name From Config or create new? TO DO
        containerName = "temp"
        #Create Blob Service Client from connectionString
        blob_service_client = BlobServiceClient.from_connection_string(connectionString)
        #Get Container
        container_client = blob_service_client.get_container_client(containerName)
        #Get All blob from Container
        #blob_list = container_client.list_blobs()
        #for blob in blob_list:
            #print("\t" + blob.name)
        #input stream from url
        fileStreamData = urllib.request.urlopen(fullFilePath)
        # Get Tar file    
        lockboxTarFile = tarfile.open(fileobj=fileStreamData,mode="r:gz")
        for fileName in lockboxTarFile.getnames():
            #Untar to current local      
            #print("\t" + fileName)
            #lockboxTarFile.extract(sourcePath + fileName)       
            #Connect to Blob or need to create new?   
            blob = blob_service_client.get_blob_client(container=containerName,blob=fileName)
            #Upload blob to azure                   
            blob.upload_blob(fileName, overwrite=True)        
            #Remove File from local path, Fix : error directory name is invalid?
            #if os.path.exists(fileName):
                #shutil.rmtree(fileName)        
        logging.info('End untaring to Azure Blob Storage....%s', datetime.datetime.utcnow())
    except  Exception as e:
        print("Something went wrong when storing the file:" + e)
