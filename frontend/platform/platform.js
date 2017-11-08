// Define global vars.
let endpoint = "http://villa.okeanos.nl:8080";
let token = $.cookie('token');
let users;
let selectedUser;

// Check if the user is already logged in.
if (token) {
  tokenDiv.hidden = true;
  initiateFrontEnd();
} else {
  tokenDiv.hidden = false;
}

function logout() {
  // Unset the token cookie.
  $.removeCookie('token', { expires: 1, path: '/' });

  // Hide the front-end controls and show the login screen.
  frontend.hidden = true;
  tokenDiv.hidden =  false;
}

// Preparing the frontend.
function initiateFrontEnd() {
  // Load the cookie!
  token = $.cookie('token');

  // Show the new transaction div.
  frontend.hidden = false;

  // Get all the users for the autocomplete.
  $.ajax({
    "async": true,
    "crossDomain": true,
    "method": "GET",
    "headers": {
      "Authorization": token,
      "Content-Type": "application/json"
    },
    "url": endpoint + '/users/list'
  }).done( (data) => {
    users = data;
    $("#transactionTargetUser").typeahead({ source: data, afterSelect: userSelected });

    getPendingTransactions();
  });

  // Set the selected user to the global var.
  function userSelected(item) {
    selectedUser = item;
  }
}

// Get every three seconds the user list.
setTimeout(function(){ $.ajax({
  "async": true,
  "crossDomain": true,
  "method": "GET",
  "headers": {
    "Authorization": token,
    "Content-Type": "application/json"
  },
  "url": endpoint + '/users/list'
}); }, 60000);

function updatePendingTransactions () {
  $(pendingTransactionsBody).remove();
  tableBody = document.createElement("tbody");
  tableBody.id = 'pendingTransactionsBody';
  pendingTransactionsTable.appendChild(tableBody);
  getPendingTransactions();
}

function getPendingTransactions () {
  // Get all pending transactions for the authenticated user.
  $.ajax({
    "async": true,
    "crossDomain": true,
    "method": "GET",
    "headers": {
      "Authorization": token,
      "Content-Type": "application/json"
    },
    "url": endpoint + '/transactions/pending'
  }).done( (data) => {
    createPendingTransactionsTable(data);
  });
}

function createPendingTransactionsTable(data) {
  // Rewrite it to an array.
  let transactions = $.map(data, function(value, index) {
    return [{
      id: index,
      amount: value.amount,
      buyerId: value.buyerId,
      sellerId: value.sellerId,
      name: value.transactionName
    }];
  });

  // Create a table row for each pending transaction.
  transactions.forEach((transaction) => {
    // Create a row in the table for every pending transaction.
    let row = pendingTransactionsBody.insertRow(-1);
    row.id = 'row' + transaction.id;

    let colUser = row.insertCell(0);
    // Get the name of the seller from the userList.
    sellerIndex = users.map((x) => { return x.id }).indexOf(transaction.sellerId);
    colUser.innerHTML = users[sellerIndex].name;

    let colDescription = row.insertCell(1);
    colDescription.innerHTML = transaction.name;

    let colPrice = row.insertCell(2);
    // Rewrite the price to euro's.
    colPrice.innerHTML = '&euro; ' + (transaction.amount / 100).toFixed(2);

    let colApprove = row.insertCell(3);
    let approveIcon = document.createElement("button");
    approveIcon.className = "btn btn-primary btn-sm btn-outline-success";
    approveIcon.transactionId = transaction.id;
    approveIcon.setAttribute('onclick', "approveTransaction(this.transactionId)");
    colApprove.appendChild(approveIcon);
    let approveIconInner = document.createElement("i");
    approveIconInner.className = "fa fa-check";
    approveIcon.appendChild(approveIconInner);

    let colDisapprove = row.insertCell(4);
    let disapproveIcon = document.createElement("button");
    disapproveIcon.className = "btn btn-primary btn-sm btn-outline-danger";
    disapproveIcon.transactionId = transaction.id;
    disapproveIcon.setAttribute('onclick', "disapproveTransaction(this.transactionId)");
    colDisapprove.appendChild(disapproveIcon);
    let disapproveIconInner = document.createElement("i");
    disapproveIconInner.className = "fa fa-times";
    disapproveIcon.appendChild(disapproveIconInner);
  });
};

function approveTransaction(id) {
  let row = '#row' + id;
  $(row).remove();

  $.ajax({
    "async": true,
    "crossDomain": true,
    "method": "GET",
    "url": endpoint + '/transactions/approve/' + id,
    "headers": {
      "Authorization": token,
      "Content-Type": "application/json"
    },
    "data": "{}",
    "processData": false
  }).done( () => {
    console.log('Succesvol toegekend: ' + id);
  });
}

function disapproveTransaction(id) {
  let row = '#row' + id;
  $(row).remove();

  $.ajax({
    "async": true,
    "crossDomain": true,
    "method": "GET",
    "url": endpoint + '/transactions/decline/' + id,
    "headers": {
      "Authorization": token,
      "Content-Type": "application/json"
    },
    "data": "{}",
    "processData": false
  }).done( () => {
    console.log('Succesvol afgekeurd: ' + id);
  })
}

// Handle submit of new transaction form.
$("#newTransactionForm").submit(function( event ) {
  // Prevent default submit behaviour.
  event.preventDefault();

  // Prepare the data for the POST.
  let data = JSON.stringify({
    "transactionName": transactionDescription.value,
    "amount": Number(transactionPrice.value) * 100
  });

  // Preparing, executing and handling the POST-request.
  $.ajax({
    "async": true,
    "crossDomain": true,
    "method": "POST",
    "url": endpoint + '/transactions/new/' + selectedUser.id,
    "data": data,
    "headers": {
      "Authorization": token,
      "Content-Type": "application/json"
    },
    "processData": false
  }).done( (data) => {
    console.log('Jeeeej!');
    $('#newTransactionForm')[0].reset();
    $('#tradingModal').modal('hide');
    // Show an success.
    let alertSuccess = document.createElement("div");
    alertSuccess.id = 'alertSuccess';
    alertSuccess.className = 'alert alert-success';
    alertSuccess.innerHTML = 'Skittermagisch! Je transactie is ter goedkeuring aangeboden aan de koper.'
    frontend.insertBefore(alertSuccess, frontend.firstChild);
    setTimeout(function(){ $(alertSuccess).remove(); }, 3000);
  }).fail( (data) => {
    // Show an error.
    console.error(data);
    // Show an error.
    let alertError = document.createElement("div");
    alertError.id = 'alertError';
    alertError.className = 'alert alert-danger';
    alertError.innerHTML = 'Anti \'vo! Je transactie is mislukt, probeer het opnieuw.'
    frontend.insertBefore(alertError, frontend.firstChild);
    setTimeout(function(){ $(alertError).remove(); }, 3000);
  });
});

// Handle the submit of the login form.
$("#tokenForm").submit(function( event ) {
  // Prevent default submit behaviour.
  event.preventDefault();

  // Prepare the data for the POST.
  let data = JSON.stringify({"authenticationKey": tokenInput.value});

  // Preparing, executing and handling the POST-request.
  $.ajax({
    "async": true,
    "crossDomain": true,
    "method": "POST",
    "url": endpoint + '/users/authenticate',
    "data": data,
    "headers": {
      "Content-Type": "application/json"
    },
    "processData": false
  }).done( (data) => {
    // Set the token as a cookie.
    $.cookie('token', data.Token, { expires: 1, path: '/' });
    tokenDiv.hidden = true;

    // Load the frontend.
    initiateFrontEnd();
  }).fail( (data) => {
    // Show an error.
    let error = document.createElement("div");
    error.id = 'tokenError';
    error.className = "form-control-feedback";
    error.innerHTML = data.responseJSON.Error;
    tokenFormGroup.appendChild(error);
    tokenFormGroup.className = "has-danger";
  });
});
