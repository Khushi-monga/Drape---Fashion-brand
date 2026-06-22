function getCookie(name)
{
    let cookieValue = null;

    if (document.cookie && document.cookie !== "")
    {
        const cookies = document.cookie.split(";");

        for (let cookie of cookies)
        {
            cookie = cookie.trim();

            if (
                cookie.substring(
                    0,
                    name.length + 1
                ) === (name + "=")
            )
            {
                cookieValue = decodeURIComponent(
                    cookie.substring(
                        name.length + 1
                    )
                );

                break;
            }
        }
    }

    return cookieValue;
}


async function handleCredentialResponse(response)
{
    console.log("CALLBACK HIT");
    console.log(response);

    alert("Google callback reached");
    
    try
    {
        const result = await fetch(
            "/accounts/social-auth/google/",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },

                body: JSON.stringify({
                    token: response.credential
                })
            }
        );

        const data = await result.json();

        if (data.success)
        {
            window.location.href = "/";
        }
        else
        {
            alert(
                data.error ||
                "Google login failed."
            );
        }
    }
    catch (error)
    {
        console.error(error);

        alert(
            "Something went wrong."
        );
    }
}