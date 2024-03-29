var express = require('express')
var router = express.Router()
const fs = require('fs')
const path = require('path')

router.get('/', function (req, res, next) {
  try {
    let resumeInfo = fs.readFileSync(path.join(__dirname, '../public/markdown/resume.md'))
    res.send(resumeInfo)
  } catch (err) {
    console.error(err)
    res.status(500).send({ error: 'There was an error reading the file.' })
  }
})

module.exports = router
