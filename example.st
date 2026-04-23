# Pizza Order Bot - CS4031 Example
# This demonstrates StateTalk language features

state Welcome {
    prompt "Welcome to PizzaBot!"
    prompt "What is your name?"
    store input as $name (str)
    goto SizeQuestion
}

state SizeQuestion {
    prompt "Hi {$name}! What size pizza would you like?"
    prompt "1 = Small ($10)"
    prompt "2 = Medium ($15)"
    prompt "3 = Large ($20)"
    store input as $size (str)

    if $size == "1" {
        set $price = 10
        set $size_name = "Small"
        goto ToppingsQuestion
    }
    elif $size == "2" {
        set $price = 15
        set $size_name = "Medium"
        goto ToppingsQuestion
    }
    elif $size == "3" {
        set $price = 20
        set $size_name = "Large"
        goto ToppingsQuestion
    }
    else {
        prompt "Invalid choice! Please enter 1, 2, or 3."
        goto SizeQuestion
    }
    end
}

state ToppingsQuestion {
    prompt "Great! A {$size_name} pizza is ${$price}."
    prompt "Would you like extra cheese? (yes/no)"
    store input as $extra_cheese (str)

    if $extra_cheese == "yes" {
        set $price = $price + 2
        set $has_cheese = "true"
        prompt "Extra cheese added! (+$2)"
    }
    else {
        set $has_cheese = "false"
    }
    end

    goto Confirmation
}

state Confirmation {
    prompt "--- Order Summary ---"
    prompt "Name: {$name}"
    prompt "Size: {$size_name}"

    if $has_cheese == "true" {
        prompt "Extra cheese: Yes"
    }
    end

    prompt "Total: ${$price}"
    prompt "Confirm order? (yes/no)"
    store input as $confirm (str)

    if $confirm == "yes" {
        prompt "Order placed! Thank you, {$name}!"
        goto EndOrder
    }
    else {
        prompt "Order cancelled."
        goto EndOrder
    }
    end
}

state EndOrder {
    prompt "Would you like to order another pizza? (yes/no)"
    store input as $again (str)

    if $again == "yes" {
        goto SizeQuestion
    }
    else {
        prompt "Thanks for visiting PizzaBot! Goodbye!"
        goto END
    }
    end
}
