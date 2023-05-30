// Pie Chart
// Retrieve the value after gaining access to the relevant HTML tag
let food = document.getElementById('tfood').innerHTML.replace('$', '')
let entertainment = document.getElementById('tentertainment').innerHTML.replace('$', '')
let business = document.getElementById('tbusiness').innerHTML.replace('$', '')
let other = document.getElementById('tother').innerHTML.replace('$', '')
let colors = [
    '#ff80aa', '#99ffcc', '#99ffff', '#ffb3ec'
];
const ctx = document.getElementById('myChart');
new Chart(ctx, {
    type: 'pie',
    data: {
        labels: ['Food', 'Entertainment', 'Business', 'Other'],
        datasets: [{
            label: 'Amount (in dollars)',
            data: [food, entertainment, business, other],
            backgroundColor: colors,
            borderWidth: 1
        }]
    }
});
// End of Pie Chart
