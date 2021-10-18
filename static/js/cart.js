function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
}
const csrftoken = getCookie("csrftoken");
let alerttoast = document.getElementById("alert-toast");
let toast_body = document.getElementById("toast-body");
let toast = new bootstrap.Toast(alerttoast);
const shipping_cost_ele = document.getElementById("shipping-cost");
const payable_amount_ele = document.getElementById("payable_amount");
const successmsg = "Removed item form bag.";
const errormsg = "ERROR! Could not remove item";
const place_order_btn = document.getElementById('place-order');

function updateprice(price){
  let elements = document.querySelectorAll('[data-bag-totalprice]');
  let shipping_cost = 0;
  let payable_amount = price;
  if(elements)
      elements.forEach((ele)=>{ele.lastChild.textContent = price});
  if(price < 800 && price >0){
      shipping_cost_ele.innerText = 50;
      shipping_cost = 50;
  }
  else{
    shipping_cost_ele.innerText = 0;
  }
  payable_amount += shipping_cost;
  payable_amount_ele.innerText = payable_amount;
}

function updatequantity(quant){
  if(quant <= 0){
    place_order_btn.disabled = true;
  }
  else{
    place_order_btn.disabled = false;
  }
  update_nav_item_count(quant);
  let elements = document.querySelectorAll('[data-bag-totalitems]');
  if(elements)
      elements.forEach((ele)=>{ele.lastChild.textContent = quant});
}

function removefromBag(citemid) {
  const prod_div = document.querySelector(
    `[data-prod-div-citemid="${citemid}"]`
  );
  var xhr = new XMLHttpRequest();
  var url = "/api/cart/remove";
  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4 && xhr.status === 200) {
      var json = JSON.parse(xhr.responseText);
      if (json.action === "success") {
        prod_div.remove();
        const price = json.total_price;
        const quant = json.total_quant;
        toast_body.textContent = successmsg;
        alerttoast.classList.remove("bg-danger");
        alerttoast.classList.add("bg-dark");
        updateprice(price);
        updatequantity(quant);
        toast.show();
      }
    } else if (xhr.readyState === 4) {
      toast_body.textContent = errormsg;
      alerttoast.classList.add("bg-danger");
      alerttoast.classList.remove("bg-dark");
      toast.show();
    }
  };
  xhr.open("POST", url, true);
  xhr.setRequestHeader("X-CSRFToken", csrftoken);
  xhr.setRequestHeader("Content-Type", "application/json");
  let data = JSON.stringify({ citemid: citemid });
  xhr.send(data);
}

let remove_btns = document.getElementsByClassName("remove-btn");
if (remove_btns) {
  for (const remove_btn of remove_btns) {
    // remove_btns.forEach((remove_btn) => {
    remove_btn.addEventListener("click", function () {
      let citemid = this.getAttribute("data-citemid");
      removefromBag(citemid);
    });
  }
}


let select_quant_btns = document.getElementsByClassName("select-pd-quant");
if(select_quant_btns)
{
  for (const select_quant_btn of select_quant_btns) {
    select_quant_btn.addEventListener('change', function(){
      const val = parseInt(this.value);
      if(val && val>0 && val <= 5){
        const citemid = this.getAttribute("data-citemid");
        updateItemquant(citemid, val);
      }
    })
  }
}

function updateItemquant(citemid, itemquant){

  const data_item_quant= document.querySelector(`[data-item-quant="${citemid}"]`); 
  var xhr = new XMLHttpRequest();
  var url = "/api/cart/update";
  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4 && xhr.status === 200) {
      var json = JSON.parse(xhr.responseText);
      if (json.action === "success") {
        const price = json.total_price;
        const quant = json.total_quant;
        updateprice(price);
        data_item_quant.innerText = itemquant;
        updatequantity(quant);
      }
    } else if (xhr.readyState === 4) {
      toast_body.textContent = "ERROR! Could not update bag";
      alerttoast.classList.add("bg-danger");
      alerttoast.classList.remove("bg-dark");
      toast.show();
    }
  };  
  xhr.open("POST", url, true);
  xhr.setRequestHeader("X-CSRFToken", csrftoken);
  xhr.setRequestHeader("Content-Type", "application/json");
  let data = JSON.stringify({ citemid: citemid, "quant":itemquant});
  xhr.send(data);

}