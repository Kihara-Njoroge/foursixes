let pass1 = document.getElementById("pass1");
let pass2 = document.getElementById("pass2");
let letter = document.getElementById("low-validator");
let capital = document.getElementById("up-validator");
let number = document.getElementById("num-validator");
let length = document.getElementById("len-validator");
let validatepass = document.getElementById("validatepass");
let matchpass = document.getElementById("matchpass");
let submit_btn = document.getElementById("reg-submit-btn");
let phone_validator = document.getElementById('phone-validator');
let phnoip = document.getElementById('phno');

let phone_valid = false;
let low_valid = false;
let up_valid = false;
let num_valid = false;
let len_valid = false;
let p1_valid = false;
let p2_valid = false;
let is_valid = false;


phnoip.onfocus = function () {
    phone_validator.style.display = "block";
};

phnoip.onblur = function () {
    phone_validator.style.display = "none";
};

phnoip.onkeyup = function () {
    const phoneno = /^\d{10}$/;
  if(this.value.match(phoneno)){
      phone_validator.style.display = "none";
      phone_valid = true;
  }
  else{
      phone_validator.style.display = "block";
      phone_valid = false;
  }
  if (p1_valid && p2_valid && phone_valid)
        submit_btn.disabled = false;
  else
        submit_btn.disabled = true;

}

pass1.onfocus = function () {
    validatepass.style.display = "block";
};

pass1.onblur = function () {
    validatepass.style.display = "none";
};

pass1.onkeyup = function () {
    // Validate lowercase letters
    let lowerCaseLetters = /[a-z]/g;
    if (pass1.value.match(lowerCaseLetters)) {
        letter.classList.remove("text-danger");
        letter.classList.add("text-success");
        low_valid = true;
    } else {
        letter.classList.remove("text-success");
        letter.classList.add("text-danger");
        low_valid = false;
    }

    // Validate capital letters
    let upperCaseLetters = /[A-Z]/g;
    if (pass1.value.match(upperCaseLetters)) {
        capital.classList.remove("text-danger");
        capital.classList.add("text-success");
        up_valid = true;
    } else {
        capital.classList.remove("text-success");
        capital.classList.add("text-danger");
        up_valid = false;
    }

    // Validate numbers
    let numbers = /[0-9]/g;
    if (pass1.value.match(numbers)) {
        number.classList.remove("text-danger");
        number.classList.add("text-success");
        num_valid = true;
    } else {
        number.classList.remove("text-success");
        number.classList.add("text-danger");
        num_valid = false;
    }

    // Validate length
    if (pass1.value.length >= 8) {
        length.classList.remove("text-danger");
        length.classList.add("text-success");
        len_valid = true;
    } else {
        length.classList.remove("text-success");
        length.classList.add("text-danger");
        len_valid = false;
    }

    if (low_valid && up_valid && num_valid && len_valid) {
        p1_valid = true;
    }
    else {
        p1_valid = false;
    }

    if (p1_valid && p2_valid && phone_valid)
        submit_btn.disabled = false;
    else
        submit_btn.disabled = true;
};


//match both password fields
pass2.onkeyup = function () {
    if (pass1.value == pass2.value) {
        matchpass.style.display = "none";
        p2_valid = true;

    } else {
        matchpass.style.display = "block";
        p2_valid = false;
    }
    if (p1_valid && p2_valid && phone_valid)
        submit_btn.disabled = false;
    else
        submit_btn.disabled = true;
};