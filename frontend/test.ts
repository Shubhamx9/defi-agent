const { prisma } = require("./lib/prisma");

async function main() {
  const chats = await prisma.chat.findMany();
  console.log("Chats:", chats);
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
