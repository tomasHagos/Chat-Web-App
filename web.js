function loggedIn()
{
    function loadEventFunction()
    {
        var theData = JSON.parse(request.responseText);
        print(theData)
    }

    var request = new XMLHttpRequest();
    //when the response is ready call this function
    request.addEventListener("load",loadEventFunction);
    request.open("POST","/api/login")//uses the relative path
    request.setRequestHeader("Content-Type","application/json")
    request.withCredentials = true;
    var login_data = JSON.stringify({username:"Tomas"})
    request.send(login_data) //content length is automatically set 
}