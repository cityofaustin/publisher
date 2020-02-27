const AWS = require('aws-sdk');
const fs = require('fs');

// Check if a yarn /cache directory exists in S3 for your Janis Branch.
// Write output to cache_exists.tmp file that can be sourced by install_yarn_dependencies.sh script
async function checkCacheExists(janisBranch){
  const s3 = new AWS.S3();
  let headObject;

  try {
    console.log("Checking if cache exists in S3")
    const headObject = await s3.headObject({
      Bucket: "coa-publisher",
      Key: `cache/${janisBranch}/yarn.lock`,
    }).promise()

    if (headObject) {
      console.log("CACHE_EXISTS=True")
      cacheExists = "True";
    }
  } catch(e) {
    if (e.code === "NotFound") {
      console.log("CACHE_EXISTS=False")
      cacheExists = "False";
    } else {
      console.log(e)
      process.exit(1)
    }
  }
  fs.writeFileSync(`${__dirname}/cache_exists.tmp`,`CACHE_EXISTS=${cacheExists}`)
}

if (require.main === module) {
  const cacheToCheck = process.argv[2]
  checkCacheExists(cacheToCheck)
}
