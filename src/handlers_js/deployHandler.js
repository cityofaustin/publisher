const AWS = require('aws-sdk');

module.exports.handler = (event, context, cb) => {
  console.log("Hello!")
  console.log(event)
  // Create site if it doesn't exist
  // Upload S3 bucket contents to netlify using netlify-sdk
}
