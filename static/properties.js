(function() {
    'use strict';
    window.addEventListener('load', function() {
      // Fetch all the forms we want to apply custom Bootstrap validation styles to
      var forms = document.getElementsByClassName('needs-validation');
      // Loop over them and prevent submission
      var validation = Array.prototype.filter.call(forms, function(form) {
        form.addEventListener('submit', function(event) {
          if (form.checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
          }
          form.classList.add('was-validated');
        }, false);
      });
    }, false);
})();

function bmi()
    {
        let height = document.getElementById("height").value;
        let weight = document.getElementById("weight").value;

        // If nothing is inputted, don't run function
        if (height == "" || weight == "")
        {
            document.querySelector('#bmi-calc').innerHTML = '';
            return;
        }

        height /= 100;
        let total = weight / height / height;
        total = Math.round( total * 10 ) / 10;
        document.querySelector('#bmi-calc').innerHTML = '<div class="alert alert-success" role="alert"> Your BMI is ' + total + '.</div>';
}

function bmr()
    {
        let age = document.getElementById("age").value;
        let height = document.getElementById("height").value;
        let weight = document.getElementById("weight").value;
        let gender = document.getElementById("gender").value

        // If nothing is inputted, don't run function
        if (height == "" || weight == "" || age == "")
        {
            document.querySelector('#bmr-calc').innerHTML = '';
            return;
        }

        height *= 6.25;
        weight *= 10;
        age *= 5;
        let total = weight + height - age
        if (gender == "male")
        {
            total += 5;
            total = Math.round( total * 10 ) / 10;
            document.querySelector('#bmr-calc').innerHTML = '<div class="alert alert-success" role="alert"> Your BMR is ' + total + '.</div>';
        }
        else
        {
            total -= 161;
            total = Math.round( total * 10 ) / 10;
            document.querySelector('#bmr-calc').innerHTML = '<div class="alert alert-success" role="alert"> Your BMR is ' + total + '.</div>';
        }
}

function whr()
    {
        let waist = document.getElementById("waist").value;
        let hip = document.getElementById("hip").value;

        // If nothing is inputted, don't run function
        if (waist == "" || hip == "")
        {
            document.querySelector('#whr-calc').innerHTML = '';
            return;
        }

        let total = waist / hip;
        total = Math.round( total * 100 ) / 100;
        document.querySelector('#whr-calc').innerHTML = '<div class="alert alert-success" role="alert"> Your waist-to-hip ratio is ' + total + '.</div>';
}
