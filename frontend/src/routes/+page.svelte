<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';

    // Stores to track totals and orders
    const totalBurgers = writable(0);
    const totalFries = writable(0);
    const totalDrinks = writable(0);
    const orders = writable([]);
    let driveThruMessage = '';

    // Function to handle order processing
    async function handleOrder() {
        if (!driveThruMessage.trim()) return;

        try {
            const response = await fetch('http://127.0.0.1:8000/orders', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: driveThruMessage })
            });

            if (response.ok) {
                const result = await response.json();

                // Update stores with response data
                totalBurgers.set(result.total_burgers);
                totalFries.set(result.total_fries);
                totalDrinks.set(result.total_drinks);
                orders.set(result.order_history);
            } else {
                const error = await response.json();
                alert(error.detail || 'An error occurred while processing your request.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to process your request. Please try again.');
        }

        // Reset input field
        driveThruMessage = '';
    }

    // Fetch initial data on component mount
    async function fetchOrders() {
        try {
            const response = await fetch('http://127.0.0.1:8000/orders', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: '' })
            });

            if (response.ok) {
                const result = await response.json();

                // Update stores with response data
                totalBurgers.set(result.total_burgers);
                totalFries.set(result.total_fries);
                totalDrinks.set(result.total_drinks);
                orders.set(result.order_history);
            } else {
                console.error('Failed to fetch initial data:', response.statusText);
            }
        } catch (error) {
            console.error('Error fetching initial data:', error);
        }
    }

    onMount(fetchOrders);
</script>

<style>
    main {
    max-width: 700px;
    margin: 2em auto;
    padding: 2em;
    font-family: 'Arial', sans-serif;
    background: linear-gradient(135deg, #ffeb3b, #ff9800);
    border-radius: 12px;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    .counter {
    display: flex;
    justify-content: space-around;
    margin-bottom: 2em;
    }
    .counter div {
    flex: 1;
    margin: 0 1em;
    text-align: center;
    }
    .icon-box {
    background: #4caf50;
    color: #fff;
    border-radius: 50%;
    width: 100px;
    height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5em;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    margin: 0 auto;
    position: relative;
    }
    .icon-box span {
    position: absolute;
    bottom: -30px;
    right: 0px;
    background: #ff9800;
    color: #fff;
    padding: 4px 6px;
    border-radius: 12px;
    font-weight: bold;
    font-size: 1.2em;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    .input-area {
    display: flex;
    align-items: center;
    margin: 3em 0;
    }
    textarea {
    flex: 1;
    padding: 1em;
    border: 2px solid #ff9800;
    border-radius: 8px;
    font-size: 1.1em;
    resize: none;
    background: #fff3e0;
    margin-right: 1em;
    }
    .run-button {
    width: 60px;
    height: 60px;
    font-size: 1em;
    font-weight: bold;
    color: #fff;
    background: #e91e63;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.3s;
    }
    .run-button:hover {
    background: #ad1457;
    }
    .order-history {
    margin-top: 2em;
    background: #fffde7;
    padding: 1em;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .order {
    display: flex;
    justify-content: space-between;
    padding: 1em;
    margin-bottom: 0.5em;
    background: #ffecb3;
    border-radius: 8px;
    font-size: 1.1em;
    }
   </style>

<main>
    <div class="counter">
        <div class="icon-box">
            🍔
            <span>{$totalBurgers}</span>
        </div>
        <div class="icon-box">
            🍟
            <span>{$totalFries}</span>
        </div>
        <div class="icon-box">
            🥤
            <span>{$totalDrinks}</span>
        </div>
    </div>
    <div class="input-area">
        <textarea
            id="message"
            bind:value={driveThruMessage}
            placeholder="E.g., 'I want two burgers and a drink' or 'Cancel order #2'"
        ></textarea>
        <button class="run-button" on:click={handleOrder}>Run</button>
    </div>
    <div class="order-history">
        <h2 style="color: #ff6f00; font-size: 1.5em; text-align: center;">Order History</h2>
        {#each $orders as order}
        <div class="order">
            <span><strong>{order.id}</strong></span>
            <span>{order.details}</span>
        </div>
        {/each}
    </div>
</main>
