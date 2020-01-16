const AWS = require('aws-sdk');
const fs = require('fs');

async function upload(localDest, s3Location){
  const s3 = new AWS.S3();

  const fileStream = fs.createReadStream(localDest)
  fileStream.on('error', function (err) {
    if (err) { throw err; }
  });

  console.log(`Start uploading ${localDest} filestream to coa-publisher/${s3Location}`)
  fileStream
  .on('open', function () {
    var s3 = new AWS.S3();
    s3.putObject({
      Bucket: "coa-publisher",
      Key: s3Location,
      Body: fileStream,
    }, function (err) {
      if (err) { throw err; }
    });
  })
  .on('end', ()=>{
    console.log(`Finished Uploading ${localDest} to coa-publisher/${s3Location}`)
  })
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const localDest = args[0];
  const s3Location = args[1];
  upload(localDest, s3Location)
}
