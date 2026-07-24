import boto3
from pathlib import Path

path = Path(__file__).resolve().parent
client = boto3.resource('s3')

def download_data():
    bucket = client.Bucket('tfl-bikes-json')
    
    for obj in bucket.objects.all():
        key = obj.key

        destination = path/"data"/"bronze"/key

        if not destination.is_file():
            bucket.download_file(key, str(destination))
            print(f"File transferred ({key})")
        else:
            print(f"File already found ({key})")


if __name__ == "__main__":        
    download_data()