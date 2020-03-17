const NetlifyAPI = require('netlify')

async function deployToNetlify(netlifySiteName, buildDir){
  try {
    const netlifyClient = new NetlifyAPI(process.env.NETLIFY_AUTH_TOKEN)

    const sites = await netlifyClient.listSites({name: netlifySiteName})
    let netlifySiteId
    for (let i in sites) {
      site = sites[i]
      if (site.name === netlifySiteName) {
        netlifySiteId = site.id
        break
      }
    }
    if (!netlifySiteId){
      console.log(`##### Building a new site for [${netlifySiteName}].`)
      const site = await netlifyClient.createSite({body: {name: `${netlifySiteName}`}})
      netlifySiteId = site.id
    }

    console.log(`##### Deploying to netlify site [${netlifySiteName}].`)
    const deploy = await netlifyClient.deploy(netlifySiteId, buildDir)
    console.log(deploy.deploy)
    console.log(`##### Finished deploying to netlify site [${netlifySiteName}].`)
  } catch(e){
    console.log(e)
    console.log(JSON.stringify(e))
    process.exit(1)
  }
}

if (require.main === module) {
  const netlifySiteName = process.argv[2]
  const buildDir = process.argv[3]
  deployToNetlify(netlifySiteName, buildDir)
}
