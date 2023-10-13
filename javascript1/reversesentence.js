function sentencerev(sentence){
  var words = sentence.split(' ');
  var result = [];
  for(var i = 0; i < words.length; i ++){
    result.push(words[i].split('').reverse().join(''));
  }  
  return result.join(' ');
}

var sentence=prompt('write any sentence')

console.log(sentencerev(sentence));