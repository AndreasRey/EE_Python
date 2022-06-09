var fs = require('fs');
var _ = require('lodash');

var years = ["1986","1987","1988","1989","1990","1991","1992","1993","1994","1995","1996","1997","1998","1999","2000","2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021"];

var fullDataset = [];

var key = 'NER';

_.each(years, function (year) {
    var dataset = JSON.parse(fs.readFileSync(`./input/imageCount/${key}/imagesCount_${key}_${year}/values.json`));
    console.log(dataset);
    fullDataset = _.concat(fullDataset, dataset);
});

fs.writeFileSync(`./output/imageCount/${key}.json`, JSON.stringify(fullDataset));