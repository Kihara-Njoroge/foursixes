const bag_btn = document.getElementById('bag-btn');
const wlist_btn = document.getElementById('wishlist-btn');
let wlist_icon = document.getElementById('wlist-icon');
let wlist_btn_text = wlist_btn.childNodes[2];
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
let alerttoast = document.getElementById('alert-toast');
let toast_body = document.getElementById('toast-body');
let toast = new bootstrap.Toast(alerttoast);
let errormsg = 'ERROR! Could not add to bag.';
let successmsg = 'ITEM ADDED TO BAG!';
let selected_size = null;
let selected_size_btn = null;
const size_alert = document.getElementById('size-alert');
let size_btns = document.getElementsByClassName('pd-size');
const quantip = document.getElementById('pd-quant');

[...size_btns].forEach(btn => {
btn.addEventListener('click', function(){
    const size = this.getAttribute('data-size');
    this.classList.add('pd-size-selected');
    size_alert.classList.add('d-none');
    selected_size = size;
    if(selected_size_btn){
    selected_size_btn.classList.remove('pd-size-selected');
    }
    selected_size_btn = this;
})
});

function wlistProdtoggle(uqid){
    var xhr = new XMLHttpRequest();
    var url = "/api/wlist/toggle";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var json = JSON.parse(xhr.responseText);
            if(json.is_success){
                if(json.action == 'add'){
                wlist_btn_text.textContent = 'Wishlisted';
                wlist_icon.classList.toggle('bi-suit-heart');
                wlist_icon.classList.toggle('bi-suit-heart-fill');
                }
                else if(json.action == 'remove'){
                wlist_btn_text.textContent = 'Wishlist';
                wlist_icon.classList.toggle('bi-suit-heart-fill');
                wlist_icon.classList.toggle('bi-suit-heart');
                }
            }
        }
};
var data = JSON.stringify({"uqid": uqid});
xhr.send(data)
}

function addtoBag(uqid, selected_size, quant,btn){
    var xhr = new XMLHttpRequest();
    var url = "/api/cart/add";
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var json = JSON.parse(xhr.responseText);
            if(json.action === 'success'){
                toast_body.textContent = successmsg;
                alerttoast.classList.remove('bg-danger');
                alerttoast.classList.add('bg-dark');
                toast.show();
                const total_quant = json.total_quant;
                update_nav_item_count(total_quant);
            }
            btn.disabled = false;
        }
        else if(xhr.readyState === 4){
            toast_body.textContent = errormsg;
            alerttoast.classList.add('bg-danger');
            alerttoast.classList.remove('bg-dark');
            toast.show();
            btn.disabled = false;
        }
        else{
            btn.disabled = true;
        }
    };
    xhr.open("POST", url, true);
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    xhr.setRequestHeader("Content-Type", "application/json");
    let data = JSON.stringify({"uqid": uqid, "size":selected_size, "quant":quant});
    xhr.send(data);
}

// if(wlist_btn){
// wlist_btn.addEventListener('click', function(){
//     if(is_loggedin){
//     let uqid = this.getAttribute('data-uqid');
//     wlistProdtoggle(uqid);
//     }
//     else{
//     location.href = "{% url 'accounts:login' %}?next={{request.path}} ";
//     }
// })
// }
      
if(bag_btn){
bag_btn.addEventListener('click', function(){
    const quant = parseInt(quantip.value);
    if(selected_size == null){
    size_alert.classList.remove('d-none');
    }
    else if(quant && quant <=5 && quant >0){
        let uqid = this.getAttribute('data-uqid');
        addtoBag(uqid, selected_size, quant, this);
    }
})
}