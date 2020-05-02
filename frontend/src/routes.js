const Imprint = () => import('@/views/Imprint.vue');
const DataProtection = () => import('@/views/DataProtection.vue');

const Login = () => import('@/views/Login.vue');
const Register = () => import('@/views/Register.vue');
const Logout = () => import('@/views/Logout.vue');
const NotFound = () => import('@/views/NotFound.vue');
const FoundFirstCompany = () => import('@/views/FoundFirstCompany.vue');
const Welcome = () => import('@/views/Welcome.vue');

const Companies = () => import('@/views/market/Companies.vue');
const LiveOrders = () => import('@/views/market/LiveOrders.vue');
const YourOrders = () => import('@/views/market/UserOrders.vue');
const MarketTrades = () => import('@/views/market/MarketTrades.vue');
const Bonds = () => import('@/views/market/Bonds.vue');
const Order = () => import('@/views/market/Order.vue');

const Trades = () => import('@/views/company/Trades.vue');
const Company = () => import('@/views/company/Company.vue');
const StatementOfAccount = () => import('@/views/company/StatementOfAccount.vue');
const Shareholders = () => import('@/views/company/Shareholders.vue');
const Depot = () => import('@/views/company/Depot.vue');
const Orderbook = () => import('@/views/company/Orderbook.vue');
const BuyerSeller = () => import('@/views/company/BuyerSeller.vue');
const CompanyArticles = () => import('@/views/company/CompanyArticles.vue');

const Newspaper = () => import('@/views/social/Newspaper.vue');
const Forum = () => import('@/views/social/Forum.vue');
const ThreadDetail = () => import('@/views/social/ThreadDetail.vue');

const Notifications = () => import('@/views/social/Notifications.vue');
const NotificationDetail = () => import('@/views/social/NotificationDetail.vue');

const Messages = () => import('@/views/social/Messages.vue');
const MessageDetail = () => import('@/views/social/MessageDetail.vue');

const Chat = () => import('@/views/social/Chat.vue');
const Profile = () => import('@/views/social/Profile.vue');

const Fonds = () => import('@/views/social/Fonds.vue');
const FondDetail = () => import('@/views/social/FondDetail.vue');
const FondApplication = () => import('@/views/social/FondApplication');

export default [
  { path: '/', name: 'home', component: Welcome },


  // auth urls
  {
    path: '/logout', name: 'logout', component: Logout, meta: { requiresAuth: true },
  },
  {
    path: '/found/first/company',
    name: 'foundFirstCompany',
    component: FoundFirstCompany,
    meta: { requiresAuth: true },
  },
  {
    path: '/notifications',
    name: 'notifications',
    component: Notifications,
    meta: { requiresAuth: true },
  },
  {
    path: '/notification/:id/',
    name: 'notificationDetail',
    component: NotificationDetail,
    meta: { requiresAuth: true },
  },
  {
    path: '/messages', name: 'messages', component: Messages, meta: { requiresAuth: true },
  },
  {
    path: '/message/:id/',
    name: 'messageDetail',
    component: MessageDetail,
    meta: { requiresAuth: true },
  },

  // None auth urls
  { path: '/login', name: 'login', component: Login },
  { path: '/register', name: 'register', component: Register },

  { path: '/company/:isin/', name: 'company', component: Company },
  {
    path: '/company/:isin/statement_of_account',
    name: 'statementOfAccount',
    component: StatementOfAccount,
    props: true,
  },
  {
    path: '/company/:isin/trades/', name: 'tradesCompany', component: Trades, props: true,
  },
  {
    path: '/company/:isin/depot/', name: 'depot', component: Depot, props: true,
  },
  {
    path: '/company/:isin/orderbook/', name: 'orderbook', component: Orderbook, props: true,
  },
  {
    path: '/company/:isin/shareholders/', name: 'shareholders', component: Shareholders, props: true,
  },
  {
    path: '/company/:isin/articles/', name: 'articlesCompany', component: CompanyArticles, props: true,
  },
  {
    path: '/company/:isin/buyerSeller/', name: 'buyerSeller', component: BuyerSeller, props: true,
  },
  {
    path: '/company/:isin/order/', name: 'order', component: Order, meta: { requiresAuth: true },
  },

  { path: '/companies/', name: 'companies', component: Companies },
  { path: '/trades/', name: 'trades', component: MarketTrades },
  { path: '/orders/own', name: 'ownOrders', component: YourOrders },
  { path: '/bonds/', name: 'bonds', component: Bonds },

  { path: '/live-orders/', name: 'liveOrders', component: LiveOrders },

  { path: '/newspaper/', name: 'newspaper', component: Newspaper },
  { path: '/forum/', name: 'forum', component: Forum },
  { path: '/forum/thread/:slug/:threadId', name: 'thread', component: ThreadDetail },


  { path: '/chat', name: 'chat', component: Chat },

  { path: '/profile/:id', name: 'profile', component: Profile },

  { path: '/fonds', name: 'fonds', component: Fonds },
  { path: '/fonds/:id', name: 'fondDetail', component: FondDetail },

  {
    path: '/fonds/:id/forum/thread/:slug/:threadId', name: 'threadFond', component: ThreadDetail, meta: { requiresAuth: true },
  },

  {
    path: '/fonds/:id/application', name: 'applicationFond', component: FondApplication, meta: { requiresAuth: true },
  },

  { path: '/data-protection', name: 'dataProtection', component: DataProtection },
  { path: '/imprint', name: 'imprint', component: Imprint },
  { path: '/404', component: NotFound },
  { path: '*', redirect: '/404' },
];
