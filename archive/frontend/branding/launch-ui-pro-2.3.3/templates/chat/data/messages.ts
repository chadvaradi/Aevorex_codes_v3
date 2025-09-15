export interface Message {
  id: string;
  chatId: string;
  content: string;
  sender: "user" | "ai";
  timestamp: string;
  imageSrc?: string; // Optional field for image source
}

// Mock messages for each chat
export const messages: Record<string, Message[]> = {
  chat1: [
    {
      id: "msg1-1",
      chatId: "chat1",
      content:
        "I need help building a responsive website for my business. It's a small e-commerce store selling handmade crafts.",
      sender: "user",
      timestamp: "2025-03-17T09:15:00Z",
    },
    {
      id: "msg1-2",
      chatId: "chat1",
      content:
        "I'd be happy to help you with your e-commerce website! To create a responsive website for your handmade crafts business, we can use modern web technologies like React, Next.js, or even a simpler stack depending on your needs. Would you like me to outline some options with their pros and cons?",
      sender: "ai",
      timestamp: "2025-03-17T09:15:30Z",
    },
    {
      id: "msg1-3",
      chatId: "chat1",
      content:
        "Yes, please. I'm not very technical, so I need something that's easy to maintain and update with new products.",
      sender: "user",
      timestamp: "2025-03-17T09:20:00Z",
    },
    {
      id: "msg1-4",
      chatId: "chat1",
      content:
        "In that case, I'd recommend using a platform like Shopify or Wix for your e-commerce store. These platforms offer:\n\n1. **User-friendly interfaces** - No coding required to add or update products\n2. **Built-in responsive design** - Looks great on all devices\n3. **Integrated payment processing** - Easy to set up and secure\n4. **SEO features** - Help customers find your store\n5. **Custom domain options** - Use your own business name\n\nShopify is particularly good for e-commerce and has themes specifically designed for showcasing handmade products. Would you like more specific information about setting up a Shopify store?",
      sender: "ai",
      timestamp: "2025-03-17T09:21:00Z",
    },
    {
      id: "msg1-5",
      chatId: "chat1",
      content:
        "Shopify sounds good. How much does it cost, and how difficult is the initial setup?",
      sender: "user",
      timestamp: "2025-03-17T09:24:00Z",
    },
    {
      id: "msg1-6",
      chatId: "chat1",
      content:
        "Shopify pricing starts at $29/month for their Basic plan, which includes everything you need to start selling. They also offer a 14-day free trial so you can test it before committing.\n\nAs for the setup process, it's quite straightforward:\n\n1. **Sign up** - Create an account with your email\n2. **Choose a theme** - Select from free or paid designs (many are under $200 as a one-time cost)\n3. **Customize your store** - Add your logo, colors, and brand elements\n4. **Add products** - Upload photos and descriptions of your crafts\n5. **Set up payment** - Connect to payment processors like Stripe or PayPal\n6. **Set up shipping** - Define your shipping rates and policies\n\nThe whole process can be completed in a weekend if you have your product details and photos ready. Shopify also has excellent customer support and extensive documentation to help you with any questions during setup.",
      sender: "ai",
      timestamp: "2025-03-17T09:25:30Z",
    },
    {
      id: "msg1-7",
      chatId: "chat1",
      content:
        "That sounds manageable. Do you think I should hire someone to set it up initially, or can I do it myself?",
      sender: "user",
      timestamp: "2025-03-17T09:28:00Z",
    },
    {
      id: "msg1-8",
      chatId: "chat1",
      content:
        "For a small handmade crafts business, you can absolutely set up Shopify yourself, especially if you're comfortable with:\n\n- Using web-based tools and applications\n- Taking and editing basic product photos\n- Writing product descriptions\n- Learning new platforms through tutorials\n\nThe advantage of doing it yourself is that you'll know how to make updates and changes later on.\n\nHowever, if any of these aspects feel overwhelming, or if you want a more customized look beyond the standard themes, hiring help might be worthwhile. You could consider:\n\n1. **A Shopify expert** - For complete setup ($500-1500 typically)\n2. **A photographer** - Just for product photos\n3. **A copywriter** - Just for product descriptions\n\nMany small business owners start by setting up the basics themselves and then hire specialized help for specific aspects they want to improve. Would you like me to suggest some resources for learning to set up Shopify yourself?",
      sender: "ai",
      timestamp: "2025-03-17T09:30:00Z",
    },
    {
      id: "msg1-9",
      chatId: "chat1",
      content:
        "Yes, please share some resources. I think I'll try to set it up myself first and see how far I get.",
      sender: "user",
      timestamp: "2025-03-17T09:33:00Z",
    },
    {
      id: "msg1-10",
      chatId: "chat1",
      content:
        "That's a great approach! Here are some excellent resources to help you set up your Shopify store:\n\n**Official Resources:**\n- [Shopify's Getting Started Guide](https://help.shopify.com/en/manual/intro-to-shopify)\n- [Shopify YouTube Tutorial Channel](https://www.youtube.com/shopify)\n- [Shopify Academy](https://www.shopify.com/learn/courses) - Free courses on setting up your store\n\n**Helpful Third-Party Tutorials:**\n- [Shopify Essential Training on LinkedIn Learning](https://www.linkedin.com/learning/shopify-essential-training)\n- [WPCrafter's Shopify Tutorial for Beginners](https://www.youtube.com/watch?v=KL7FuRc_7M4)\n\n**Communities for Questions:**\n- [Shopify Community Forums](https://community.shopify.com/)\n- r/shopify on Reddit\n\n**For Product Photography:**\n- [Shopify's DIY Product Photography Guide](https://www.shopify.com/blog/12206313-the-ultimate-diy-guide-to-beautiful-product-photography)\n\nStart with Shopify's own getting started guide, and use the YouTube tutorials when you need to see something demonstrated visually. The community forums are great when you have specific questions.\n\nWould you like specific tips for showcasing handmade crafts effectively on your store?",
      sender: "ai",
      timestamp: "2025-03-17T09:35:00Z",
    },
    {
      id: "msg1-11",
      chatId: "chat1",
      content:
        "Yes, I would love some tips for showcasing handmade items effectively!",
      sender: "user",
      timestamp: "2025-03-17T09:38:00Z",
    },
    {
      id: "msg1-12",
      chatId: "chat1",
      content:
        "Here are some specialized tips for showcasing handmade crafts on your e-commerce store:\n\n**Photography Tips:**\n1. **Show scale** - Include something in photos that shows the size of your items\n2. **Capture details** - Close-ups of intricate work show craftsmanship\n3. **Show items in use** - People visualize owning items better when they see them in context\n4. **Consistent style** - Use similar lighting and backgrounds for a cohesive look\n5. **Multiple angles** - 4-6 photos per item showing different perspectives\n\n**Product Descriptions:**\n1. **Tell your creation story** - Share your process or inspiration\n2. **Describe materials** - Highlight quality and sourcing\n3. **Mention dimensions precisely** - All measurements customers might need\n4. **Care instructions** - How to maintain the item\n5. **Personalization options** - If you offer customization\n\n**Store Organization:**\n1. **Logical collections** - Group similar items together\n2. **Highlight bestsellers** - Feature your most popular items prominently\n3. **Seasonal collections** - Rotate featured items based on seasons/holidays\n\n**Building Trust:**\n1. **About the Artist page** - Share your story and passion\n2. **Process photos or videos** - Show items being made\n3. **Detailed policies** - Clear shipping, returns, and custom order policies\n4. **Highlight reviews** - Feature customer testimonials prominently\n\nThese elements help customers connect with handmade items emotionally, which is often why they choose handmade over mass-produced alternatives.",
      sender: "ai",
      timestamp: "2025-03-17T09:40:00Z",
    },
    {
      id: "msg1-13",
      chatId: "chat1",
      content:
        "These are excellent tips, thank you! I think I have enough to get started now.",
      sender: "user",
      timestamp: "2025-03-17T09:44:00Z",
    },
    {
      id: "msg1-14",
      chatId: "chat1",
      content:
        "You're welcome! Good luck with your handmade crafts store. Remember to start small and build up your store as you go - you don't need to have everything perfect from day one. Feel free to reach out if you have more questions as you set up your Shopify store or need advice on specific aspects of your e-commerce business. Happy crafting and selling!",
      sender: "ai",
      timestamp: "2025-03-17T09:45:00Z",
    },
  ],
  chat2: [
    {
      id: "msg2-1",
      chatId: "chat2",
      content:
        "Can you explain how useEffect works in React? I'm having trouble understanding when it runs and what the dependency array does.",
      sender: "user",
      timestamp: "2025-03-16T14:22:00Z",
    },
    {
      id: "msg2-2",
      chatId: "chat2",
      content:
        "I'd be happy to explain how useEffect works in React!\n\nThe useEffect hook lets you perform side effects in function components. Side effects are operations that affect something outside the scope of the function being executed, like:\n- Data fetching\n- Setting up subscriptions\n- Manually changing the DOM\n- Logging\n\n**Basic Syntax:**\n```jsx\nuseEffect(() => {\n  // Your effect code here\n  \n  // Optional cleanup function\n  return () => {\n    // Cleanup code here\n  };\n}, [dependency1, dependency2]);\n```\n\n**When useEffect Runs:**\n\n1. **After render:** useEffect runs after the component renders (including the first render)\n2. **After DOM updates:** It waits for the browser to paint the screen\n3. **Before unmount:** If you return a cleanup function, it runs before the component unmounts\n\n**The Dependency Array:**\nThe second argument to useEffect is the dependency array, which controls when the effect runs:\n\n- **Empty array `[]`:** The effect runs only once after the initial render\n- **With dependencies `[dep1, dep2]`:** The effect runs after the initial render AND after any render where the listed dependencies have changed\n- **No dependency array:** The effect runs after every render\n\nReact compares dependencies using Object.is comparison (similar to ===).\n\nWould you like me to provide some examples of different dependency array scenarios?",
      sender: "ai",
      timestamp: "2025-03-16T14:23:00Z",
    },
    {
      id: "msg2-3",
      chatId: "chat2",
      content:
        "Yes, examples would be helpful. Especially showing what happens with different dependency arrays.",
      sender: "user",
      timestamp: "2025-03-16T14:25:00Z",
    },
    {
      id: "msg2-4",
      chatId: "chat2",
      content:
        "Here are examples of useEffect with different dependency arrays:\n\n**Example 1: No Dependency Array (runs after every render)**\n```jsx\nfunction ExampleComponent() {\n  const [count, setCount] = useState(0);\n  \n  useEffect(() => {\n    console.log('This runs after EVERY render');\n  }); // No dependency array\n  \n  return (\n    <div>\n      <p>Count: {count}</p>\n      <button onClick={() => setCount(count + 1)}>Increment</button>\n    </div>\n  );\n}\n```\nIn this example, the effect runs after every render, including the first render and any time you click the button.\n\n**Example 2: Empty Dependency Array (runs once)**\n```jsx\nfunction ExampleComponent() {\n  const [count, setCount] = useState(0);\n  \n  useEffect(() => {\n    console.log('This runs ONLY after the first render');\n  }, []); // Empty dependency array\n  \n  return (\n    <div>\n      <p>Count: {count}</p>\n      <button onClick={() => setCount(count + 1)}>Increment</button>\n    </div>\n  );\n}\n```\nThis effect only runs once after the component mounts. Clicking the button won't trigger the effect again.\n\n**Example 3: With Dependencies (runs conditionally)**\n```jsx\nfunction ExampleComponent() {\n  const [count, setCount] = useState(0);\n  const [name, setName] = useState('React');\n  \n  useEffect(() => {\n    console.log(`Count changed to: ${count}`);\n  }, [count]); // Only runs when count changes\n  \n  return (\n    <div>\n      <p>Count: {count}</p>\n      <button onClick={() => setCount(count + 1)}>Increment Count</button>\n      <p>Name: {name}</p>\n      <button onClick={() => setName('UseEffect')}>Change Name</button>\n    </div>\n  );\n}\n```\nThis effect runs after the first render and whenever the count value changes. Changing the name won't trigger the effect.\n\n**Example 4: Cleanup Function**\n```jsx\nfunction ExampleComponent() {\n  const [isOnline, setIsOnline] = useState(true);\n  \n  useEffect(() => {\n    // Setup effect\n    console.log('Setting up subscription');\n    const timer = setTimeout(() => {\n      console.log('Timer executed');\n    }, 1000);\n    \n    // Cleanup function\n    return () => {\n      console.log('Cleaning up subscription');\n      clearTimeout(timer);\n    };\n  }, [isOnline]); // Runs when isOnline changes\n  \n  return (\n    <div>\n      <p>Status: {isOnline ? 'Online' : 'Offline'}</p>\n      <button onClick={() => setIsOnline(!isOnline)}>Toggle Status</button>\n    </div>\n  );\n}\n```\nIn this example:\n- When the component first renders, \"Setting up subscription\" is logged\n- When the status changes, the cleanup function runs first (\"Cleaning up subscription\"), then the effect runs again\n- When the component unmounts, the cleanup function runs one last time\n\nDid these examples help clarify how the dependency array works?",
      sender: "ai",
      timestamp: "2025-03-16T14:28:00Z",
    },
    {
      id: "msg2-5",
      chatId: "chat2",
      content:
        "Yes, this is much clearer now! One more question - what are some common mistakes with useEffect that I should avoid?",
      sender: "user",
      timestamp: "2025-03-16T14:32:00Z",
    },
    {
      id: "msg2-6",
      chatId: "chat2",
      content:
        "Great question! Here are common useEffect mistakes to avoid:\n\n**1. Missing Dependencies**\n```jsx\n// ❌ INCORRECT\nuseEffect(() => {\n  console.log(user.name);\n}, []); // Missing dependency\n\n// ✅ CORRECT\nuseEffect(() => {\n  console.log(user.name);\n}, [user.name]); // Properly listed dependency\n```\nForgetting dependencies can cause stale closures and bugs that are hard to track down.\n\n**2. Object/Array Dependencies Without Memoization**\n```jsx\n// ❌ PROBLEMATIC\nconst options = { id: user.id };\nuseEffect(() => {\n  fetchData(options);\n}, [options]); // options is recreated every render\n\n// ✅ BETTER\nconst options = useMemo(() => ({ id: user.id }), [user.id]);\nuseEffect(() => {\n  fetchData(options);\n}, [options]);\n\n// ✅ ALSO GOOD\nuseEffect(() => {\n  fetchData({ id: user.id });\n}, [user.id]); // Reference the primitive value directly\n```\nNew object/array references on every render will cause useEffect to run unnecessarily.\n\n**3. Function Dependencies Without useCallback**\n```jsx\n// ❌ PROBLEMATIC\nconst handleData = (data) => {\n  // Process data\n};\nuseEffect(() => {\n  fetchData().then(handleData);\n}, [handleData]); // Function recreated every render\n\n// ✅ BETTER\nconst handleData = useCallback((data) => {\n  // Process data\n}, []); // Stable function reference\nuseEffect(() => {\n  fetchData().then(handleData);\n}, [handleData]);\n```\n\n**4. Infinite Loop with State Updates**\n```jsx\n// ❌ INFINITE LOOP\nuseEffect(() => {\n  setCount(count + 1);\n}); // No dependency array\n\n// ✅ CONTROLLED UPDATE\nuseEffect(() => {\n  setCount(count + 1);\n}, []); // Only runs once after mount\n\n// ✅ OR WITH FUNCTIONAL UPDATE\nuseEffect(() => {\n  setCount(prevCount => prevCount + 1);\n}, []); // Safer approach\n```\n\n**5. Side Effects in Render**\n```jsx\n// ❌ INCORRECT\nfunction Component() {\n  fetch('/api/data'); // Side effect in render\n  return <div>Data</div>;\n}\n\n// ✅ CORRECT\nfunction Component() {\n  useEffect(() => {\n    fetch('/api/data');\n  }, []);\n  return <div>Data</div>;\n}\n```\n\n**6. Not Cleaning Up Properly**\n```jsx\n// ❌ MEMORY LEAK\nuseEffect(() => {\n  const subscription = subscribe();\n  // No cleanup\n}, []);\n\n// ✅ PROPER CLEANUP\nuseEffect(() => {\n  const subscription = subscribe();\n  return () => {\n    subscription.unsubscribe();\n  };\n}, []);\n```\n\n**7. Using Async Functions Directly**\n```jsx\n// ❌ INCORRECT\nuseEffect(async () => { // Can't use async directly\n  const data = await fetchData();\n  setData(data);\n}, []);\n\n// ✅ CORRECT\nuseEffect(() => {\n  const getData = async () => {\n    const data = await fetchData();\n    setData(data);\n  };\n  getData();\n}, []);\n```\n\nKeeping these common pitfalls in mind will help you use useEffect more effectively and avoid hard-to-debug issues in your React applications.",
      sender: "ai",
      timestamp: "2025-03-16T14:36:00Z",
    },
    {
      id: "msg2-7",
      chatId: "chat2",
      content:
        "This is incredibly helpful. Thank you for the detailed explanation and examples!",
      sender: "user",
      timestamp: "2025-03-16T14:39:00Z",
    },
    {
      id: "msg2-8",
      chatId: "chat2",
      content:
        "You're welcome! I'm glad I could help clarify useEffect for you. It's one of the most powerful hooks in React, but it can be tricky to master. \n\nIf you have any more questions about React hooks or front-end development in general, feel free to ask. Good luck with your React projects!",
      sender: "ai",
      timestamp: "2025-03-16T14:40:00Z",
    },
  ],
  // Empty chat for showing the initial state
  empty: [],
};

// Get messages for a specific chat
export const getMessagesByChatId = (chatId: string): Message[] => {
  return messages[chatId] || [];
};

// Add a new message to a chat
export const addMessage = (
  chatId: string,
  content: string,
  sender: "user" | "ai",
): Message => {
  const newMessage: Message = {
    id: `msg-${Date.now()}`,
    chatId,
    content,
    sender,
    timestamp: new Date().toISOString(),
  };

  if (!messages[chatId]) {
    messages[chatId] = [];
  }

  messages[chatId].push(newMessage);
  return newMessage;
};

// Generate a mock AI response
export const generateMockAiResponse = (
  chatId: string,
  userMessage: string,
): Promise<Message> => {
  return new Promise((resolve) => {
    // Simulate API delay
    setTimeout(() => {
      // Default response
      let response =
        "I'm not sure how to respond to that. Can you provide more details?";
      let imageSrc: string | undefined = undefined;

      // Check for specific prompts
      if (userMessage.toLowerCase().includes("tokyo")) {
        response = `Best times to travel are during spring (March-May) for cherry blossoms or fall (Sept-Nov) for autumn colors. Would you like me to provide more specific flight options based on your departure city?`;
      } else if (userMessage.toLowerCase().includes("image")) {
        response =
          "I've created an abstract image of melting waves in pastel pearl colors. The composition features fluid, undulating forms that evoke the sensation of waves in motion, rendered in soft pearlescent pastels that blend into one another.";
        imageSrc = "/ai-image.jpeg";
      } else if (userMessage.toLowerCase().includes("invitation")) {
        response =
          "You're cordially invited to a charming afternoon in the garden! Join us on Saturday, June 15th, 2024 from 3:00 PM - 7:00 PM at Maddison Street 23. Garden casual attire. Please join us for an afternoon of refreshing beverages, delightful treats, and wonderful company amidst the blooming flowers.";
      }
      // Keep existing responses
      else if (
        userMessage.toLowerCase().includes("hello") ||
        userMessage.toLowerCase().includes("hi")
      ) {
        response = "Hello! How can I assist you today?";
      } else if (userMessage.toLowerCase().includes("help")) {
        response =
          "I'd be happy to help! What specific information or assistance do you need?";
      } else if (userMessage.toLowerCase().includes("thank")) {
        response = "You're welcome! Is there anything else you'd like to know?";
      } else if (
        userMessage.toLowerCase().includes("code") ||
        userMessage.toLowerCase().includes("programming")
      ) {
        response =
          "I can help with programming questions. What language or framework are you working with?";
      } else if (userMessage.length < 10) {
        response = "Could you elaborate a bit more so I can better assist you?";
      }

      const aiMessage = addMessage(chatId, response, "ai");

      // Add image source if available
      if (imageSrc) {
        aiMessage.imageSrc = imageSrc;
      }

      resolve(aiMessage);
    }, 5000);
  });
};

// Helper function to generate mock AI response without modifying global store
export const createMockAiResponse = (
  chatId: string,
  userMessage: string,
): Promise<Message> => {
  return new Promise((resolve) => {
    // Simulate API delay
    setTimeout(() => {
      // Default response
      let response =
        "I'm not sure how to respond to that. Can you provide more details?";
      let imageSrc: string | undefined = undefined;

      // Check for specific prompts
      if (
        userMessage
          .toLowerCase()
          .includes("find the best flights for my next trip to tokyo")
      ) {
        response = `Here are some recommended flights to Tokyo:

1. **Japan Airlines (JAL)** - Direct flights from major international airports with excellent service.
2. **All Nippon Airways (ANA)** - Premium experience with competitive prices.
3. **Singapore Airlines** - Great connection options with a stopover in Singapore.

Best times to travel are during spring (March-May) for cherry blossoms or fall (Sept-Nov) for autumn colors. 

Would you like me to provide more specific flight options based on your departure city?`;
      } else if (
        userMessage
          .toLowerCase()
          .includes(
            "generate an abstract image of melting waves in pastel pearl colors",
          )
      ) {
        response =
          "I've created an abstract image of melting waves in pastel pearl colors. The composition features fluid, undulating forms that evoke the sensation of waves in motion, rendered in soft pearlescent pastels that blend into one another.";
        imageSrc = "/ai-image.jpeg";
      } else if (
        userMessage
          .toLowerCase()
          .includes("prepare an invitation for a garden party at my house")
      ) {
        response = `**Garden Party Invitation**

You're cordially invited to a charming afternoon in the garden!

**Date**: Saturday, June 15th, 2024
**Time**: 3:00 PM - 7:00 PM
**Location**: The Gardens at [Your Address]
**Attire**: Garden Casual

Please join us for an afternoon of refreshing beverages, delightful treats, and wonderful company amidst the blooming flowers.

RSVP by June 1st
[Your Contact Information]

*Note: The event will be held outdoors, weather permitting.*`;
      }
      // Keep existing responses
      else if (
        userMessage.toLowerCase().includes("hello") ||
        userMessage.toLowerCase().includes("hi")
      ) {
        response = "Hello! How can I assist you today?";
      } else if (userMessage.toLowerCase().includes("help")) {
        response =
          "I'd be happy to help! What specific information or assistance do you need?";
      } else if (userMessage.toLowerCase().includes("thank")) {
        response = "You're welcome! Is there anything else you'd like to know?";
      } else if (
        userMessage.toLowerCase().includes("code") ||
        userMessage.toLowerCase().includes("programming")
      ) {
        response =
          "I can help with programming questions. What language or framework are you working with?";
      } else if (userMessage.length < 10) {
        response = "Could you elaborate a bit more so I can better assist you?";
      }

      // Create the AI message object
      const aiMessage: Message = {
        id: `msg-${Date.now()}-$1000`, // More unique ID
        chatId,
        content: response,
        sender: "ai",
        timestamp: new Date().toISOString(),
      };

      // Add image source if available
      if (imageSrc) {
        aiMessage.imageSrc = imageSrc;
      }

      resolve(aiMessage);
    }, 3000);
  });
};
