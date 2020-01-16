const AWS = require('aws-sdk');
const fs = require('fs');

async function download(s3Location, localDest){
  const s3 = new AWS.S3();

  let file = fs.createWriteStream(localDest);

  s3.getObject({
    Bucket: "coa-publisher",
    Key: s3Location,
  })
  .createReadStream()
  .on('end', () => {
    console.log(`Finished Downloading coa-publisher/${s3Location} to ${localDest}`)
  })
  .on('error', (err) => {
    throw err;
  }).pipe(file);
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const s3Location = args[0];
  const localDest = args[1];
  download(s3Location, localDest)
}
