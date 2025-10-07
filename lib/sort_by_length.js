function sortByLengthAscending(array) {
    return array.sort((x,y) => x.length - y.length);
}
function sortByLengthDescending (array) {
    return array.sort((x,y) => y.length - x.length);
}

export {sortByLengthAscending, sortByLengthDescending};