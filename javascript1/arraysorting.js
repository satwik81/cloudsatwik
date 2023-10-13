let input = prompt("Enter a list of numbers separated by commas:");
let array = input.split(",");
array.sort(function(a,b){return a-b})
console.log(array);