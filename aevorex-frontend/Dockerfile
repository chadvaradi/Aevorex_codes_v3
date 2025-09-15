# Build stage
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Set build-time environment variables
ARG NEXT_PUBLIC_CALENDLY_URL
ENV NEXT_PUBLIC_CALENDLY_URL=$NEXT_PUBLIC_CALENDLY_URL

RUN npm run build

# Run stage
FROM node:18 AS runner
WORKDIR /app
ENV NODE_ENV production
ENV PORT 8080
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 8080
CMD ["npm", "start"]