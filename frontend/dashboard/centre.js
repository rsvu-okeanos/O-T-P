let host = 'http://localhost'
let labels = [];
let priceHistory = {};

let chartData = {
    labels: labels,
    datasets: []
};

let colorSet = [
  {primary: '#F44336', secondary: '#E57373'}, // 1
  {primary: '#E91E63', secondary: '#F06292'}, // 2
  {primary: '#9C27B0', secondary: '#BA68C8'}, // 3
  {primary: '#673AB7', secondary: '#9575CD'}, // 4
  {primary: '#3F51B5', secondary: '#7986CB'}, // 5
  {primary: '#2196F3', secondary: '#64B5F6'}, // 6
  {primary: '#03A9F4', secondary: '#4FC3F7'}, // 7
  {primary: '#00BCD4', secondary: '#4DD0E1'}, // 8
  {primary: '#009688', secondary: '#4DB6AC'}, // 9
  {primary: '#4CAF50', secondary: '#81C784'}, // 10
  {primary: '#8BC34A', secondary: '#AED581'}, // 11
  {primary: '#CDDC39', secondary: '#DCE775'}, // 12
  {primary: '#FFEB3B', secondary: '#FFF176'}, // 13
  {primary: '#FFC107', secondary: '#FFD54F'}, // 14
]

class DataSetItem {
  constructor(label, id, primaryColor, secondaryColor) {
    this.label = label;
    this.fill = false;
    this.lineTension = 0.1;
    this.backgroundColor = primaryColor;
    this.borderColor = primaryColor;
    this.borderCapStyle = 'butt';
    this.borderDashOffset = 0.0;
    this.borderJoinStyle = 'miter';
    this.pointBorderColor = primaryColor;
    this.pointBackgroundColor = "#fff";
    this.pointBorderWidth = 1;
    this.pointHoverRadius = 5;
    this.pointHoverBackgroundColor = secondaryColor;
    this.pointHoverBorderColor = primaryColor;
    this.pointHoverBorderWidth = 2;
    this.pointRadius = 1;
    this.pointHitRadius = 10;
    this.data = priceHistory[id];
    this.spanGaps = false;
  }
}

// This code loads the IFrame Player API code asynchronously.
let tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
let firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// This code loads the products and prepare the presentation layer.
$.getJSON(host + ':80/getProducts', function(products) {
  if (products.length > 14) {
    return console.error('Too many products!');
  }

  // Sort the product by order.
  products.sort((a, b) => {
    return a.order - b.order;
  });

  // Create tables for each product.
  products.forEach((product, index) => {
    let tbody;

    // Select the right table.
    if (index <= 6) {
      tbody = document.getElementById('tableBody1');
    } else {
      tbody = document.getElementById('tableBody2');
    }

    // Create row and cells.
    let row = tbody.insertRow(-1);
    row.id = 'row' + product.id;
    let colName = row.insertCell(0);
    colName.innerHTML = product.name;
    let colPrice = row.insertCell(1);
    colPrice.id = 'price' + product.id;
    let colDeltaText = row.insertCell(2);
    colDeltaText.id = 'deltaText' + product.id;
    let colDeltaIcon = row.insertCell(3);
    let icon = document.createElement("i");
    icon.id = 'deltaIcon' + product.id;
    icon.className = "fa fa-arrow-up";
    icon.setAttribute('aria-hidden', true);
    colDeltaIcon.appendChild(icon);

    // Preparing chart.
    if (product.price < 4) {
      // Get the color array.
      let colors = colorSet[index];
      // Prepare array.
      priceHistory[product.id] = [];
      // Create a dataSetInstance
      let dataSetInstance = new DataSetItem(product.name, product.id, colors.primary, colors.secondary);
      chartData.datasets.push(dataSetInstance);
    }
  });

  // Start the big socket show!
  let event = new Event('start');
  document.dispatchEvent(event);
});

document.addEventListener('start', function() {
  console.info('Go go go!');
  let ctx = document.getElementById("chart");
  let socket = io(host + ':3000');

  let chart = new Chart(ctx, {type: 'line', data: chartData});

  socket.on('prices', function (data) {
    let amountHistoricPrices = 200;

    data.forEach((item, index) => {
      // Check if there is already an array for this productId.
      if (!(priceHistory[item.id] instanceof Array)) {
        priceHistory[item.id] = [];
      }

      // Remove the first price before adding a new one.
      if (priceHistory[item.id].length >= amountHistoricPrices) {
        priceHistory[item.id].shift();
      }

      // Push the new price to the array.
      priceHistory[item.id].push(item.price);

      // Setting the price.
      let price = document.getElementById("price" + item.id);
      price.innerHTML = "&euro; " + item.price.toFixed(2);

      // Preparing the delta-information
      let deltaIcon = document.getElementById("deltaIcon" + item.id);
      let deltaText = document.getElementById("deltaText" + item.id);

      // Set the deltaText
      deltaText.innerHTML = "&euro; " + item.delta.toFixed(2);

      // Set the deltaIcon
      if (item.delta.toFixed(2) > 0) {
        deltaIcon.className = "fa fa-arrow-up rotate";
      } else if (item.delta.toFixed(2) < 0) {
        deltaIcon.className = "fa fa-arrow-up rotate down";
      } else {
        deltaIcon.className = "fa fa-stop";
      }

      let row = document.getElementById("row" + item.id);
      if (item.vol > 0) {
        row.className = "volumeFlash";
      } else {
        row.className = "";
      }
    });

    // Remove the first price before adding a new one.
    if (labels.length < amountHistoricPrices) {
      labels.push("");
    }

    chart.update();
  });

  socket.on('video', function(video) {
    console.info('Video will start...');

    let playerContent = document.getElementById('playerContent');
    let playerElement = document.createElement("div");
    playerElement.id = 'player';
    playerContent.appendChild(playerElement);

    // Create an <iframe> (and YouTube player).
    let player = new YT.Player('player', {
        height: '936',
        width: '1664',
        videoId: video.id,
        events: {
          'onReady': onPlayerReady,
          'onStateChange': onPlayerStateChange
        },
        playerVars: {
        	controls: 0,
        	modestbranding: 1,
        	showinfo: 0,
          cc_load_policy: 1
        }
      });

    // The API will call this function when the video player is ready.
    function onPlayerReady(event) {
  		openOverlay();
  		event.target.playVideo();
    }

    // The API calls this function when the player's state changes. When player is finished, close the overlay.
    function onPlayerStateChange(event) {
      if (event.data == 0) {
      	closeOverlay();
      }
    }

    /* Open when the player is ready */
    function openOverlay() {
        document.getElementById("video").style.width = "100%";
    }

    /* Close the overlay */
    function closeOverlay() {
    	player.stopVideo();
        document.getElementById("video").style.width = "0%";
        document.getElementById("player").remove();
    }
  });
});
