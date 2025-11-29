let question=[];
let i=0;
let answers=[];
// Objective: To fetch 15 random questions from a json containing 50 questions and store them in questions array
async function questions(){
    const res=await fetch("Project.json");
    const data=await res.json();
    let used=[];
    while (question.length<15){
        let r=Math.floor(Math.random()*data.length);
        let id=data[r].id;
        let isThere=false;
        for (let x of used){
            if (x===id){
                isThere=true;
            }
        }
        if (!isThere){
            used.push(id);
            question.push(data[r]);
        }
    }
    display();
}
// Objective: Function used to display questions from the array containing questions
function display(){
    let q = question[i];
    document.getElementById("question").innerHTML="<h4>Question "+(i+1)+" of 15<br>"+q.question+"</h4>";
    if (i==0){
        document.getElementById("option").innerHTML="<div class='p-3'>"+"<label class='option-block'><input type='radio' name='opt' value='0'"+(answers[i]==0?"checked":"")+">"+q.options[0]+"</label><hr>"+"<label class='option-block'><input type='radio' name='opt' value='1'"+(answers[i]==1?"checked":"")+">"+q.options[1]+"</label><hr>"+"<label class='option-block'><input type='radio' name='opt' value='2'"+(answers[i]==2?"checked":"")+">"+q.options[2]+"</label><hr>"+"<label class='option-block'><input type='radio' name='opt' value='3'"+(answers[i]==3?"checked":"")+">"+q.options[3]+"</label>"+"</div><br>"+"<button class='btn btn-primary float-end' onclick='next()'>Next</button>";
    }
    else if (i>0&&i<14){
        document.getElementById("option").innerHTML="<div class='p-3'>"+"<label class='option-block'><input type='radio' name='opt' value='0'"+(answers[i]==0?"checked":"")+">"+q.options[0]+"</label><hr>"+"<label class='option-block'><input type='radio' name='opt' value='1'"+(answers[i]==1?"checked":"")+">"+q.options[1]+"</label><hr>"+"<label class='option-block'><input type='radio' name='opt' value='2'"+(answers[i]==2?"checked":"")+">"+q.options[2]+"</label><hr>"+"<label class='option-block'><input type='radio' name='opt' value='3'"+(answers[i]==3?"checked":"")+">"+q.options[3]+"</label>"+"</div><br>"+"<button class='btn btn-primary float-end' onclick='next()'>Next</button>" + "<button class='btn btn-primary float-start' onclick='previous()'>Previous</button>";
    }
    else if (i==14){
        document.getElementById("option").innerHTML="<div class='p-3'>"+"<label class='option-block'><input type='radio' name='opt' value='0'"+(answers[i]==0?"checked":"")+">"+q.options[0]+"</label><hr>"+"<label class='option-block'><input type='radio' name='opt' value='1'"+(answers[i]==1?"checked":"")+">"+q.options[1]+"</label><hr>"+"<label class='option-block'><input type='radio' name='opt' value='2'"+(answers[i]==2?"checked":"")+">"+q.options[2]+"</label><hr>"+"<label class='option-block'><input type='radio' name='opt' value='3'"+(answers[i]==3?"checked":"")+">"+q.options[3]+"</label>"+"</div><br>"+"<button class='btn btn-primary float-start' onclick='previous()'>Previous</button>" + "<button class='btn btn-primary float-end' onclick='submit()'>Submit</button>";
    }
}
// Objective: Function used to display the next question
function next(){
    let s=document.querySelector("input[name='opt']:checked");
    if (s){
        answers[i]=s.value;
    }
    else {
        answers[i]=null;
    }
    i++;
    if (i<15){
        display();
    }
}
// Objective: Function used to display the previous question 
function previous(){
    let s=document.querySelector("input[name='opt']:checked");
    if (s){
        answers[i]=s.value;
    }
    else {
        answers[i]=null;
    }
    i--;
    if (i<15){
        display();
    }
}
let total=0;
// Objective: Function used to show the result page when submit button is clicked
function submit(){
    let s=document.querySelector("input[name='opt']:checked");
    if (s){
        answers[i]=s.value;
    }
    else {
        answers[i]=null;
    }
    for (let x=0;x<question.length;x++){
        if (answers[x]==question[x].answer){
            total++;
        }
    }
    localStorage.setItem("score",total);
    localStorage.setItem("answers",JSON.stringify(answers));
    localStorage.setItem("questions",JSON.stringify(question));
    window.location.href="Result.html";
}
// Objective: Function to show the result of the test and show the correct answers for the questions in which the asnwers were wrong 
function result(){
    let total=localStorage.getItem("score");
    let answers=JSON.parse(localStorage.getItem("answers"));
    let questions=JSON.parse(localStorage.getItem("questions"));
    document.getElementById("Result").innerHTML="<h3 class='text-center'>Your Score: "+total+" / 15</h3>";
    let output="";
    for (let x=0;x<questions.length;x++){
        let q=questions[x];
        let userAns=answers[x];
        let correctAns=q.answer;
        let cardColor=(userAns==correctAns)?"border-success":"border-danger";
        output+="<div class='card p-3 mt-3 "+cardColor+"' style='border-width: 3px;'>";
        output+="<h5>Q"+(x+1)+". "+q.question+"</h5>";
        if (userAns===null){
            output+="<p><b>Your Answer:</b> <span class='text-secondary'>Not Attempted</span></p>";
            output+="<p><b>Correct Answer:</b> "+q.options[correctAns]+"</p>";
        }
        else{
            output+="<p><b>Your Answer:</b> "+q.options[userAns]+"</p>";
            if (userAns!=correctAns){
                output+="<p><b>Correct Answer:</b> "+q.options[correctAns]+"</p>";
            }
        }
        output+="</div>";
    }
    document.getElementById("review").innerHTML=output;
}
// Objective: Function used to change the theme of page to light or darks as per need
function theme(){
    let select=document.getElementById("theme-select").value;
    let body=document.body;
    if (select==="dark"){
        body.classList.add("bg-dark","text-light");
        body.classList.remove("bg-light","text-dark");
        document.querySelectorAll(".card").forEach(c=>{
            c.classList.add("bg-dark","text-light");
            c.classList.remove("bg-light","text-dark");
        });
    }
    else{
        body.classList.add("bg-light","text-dark");
        body.classList.remove("bg-dark","text-light");
        document.querySelectorAll(".card").forEach(c=>{
            c.classList.add("bg-light","text-dark");
            c.classList.remove("bg-dark","text-light");
        });
    }

    localStorage.setItem("theme",select);
}
// Objective: Function used to know the theme of the page selected by the user
function init(){
    let saved=localStorage.getItem("theme")||"light";
    const select=document.getElementById("theme-select");
    if (select){
        select.value=saved;
    }
    theme();
}