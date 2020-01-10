const AWS = require('aws-sdk');

// Check if a yarn /cache directory exists in S3 for your Janis Branch.
// Returns true or false
async function cacheExists(janisBranch){
  const s3 = new AWS.S3();
  let headObject;

  try {
    const headObject = await s3.headObject({
      Bucket: "coa-publisher",
      Key: `cache/${janisBranch}/yarn.lock`,
    }).promise()

    if (headObject) {
      console.log("True")
    }
  } catch(e) {
    if (e.code === "NotFound") {
      console.log("False")
    } else {
      process.exit(1)
    }
  }
}

cacheExists(process.env.JANIS_BRANCH)
