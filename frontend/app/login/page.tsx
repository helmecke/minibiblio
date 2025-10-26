import LoginForm from "../../components/LoginForm";

export default function PatronLoginPage() {
  return <LoginForm heading="Patron Login" endpoint="/auth/login" successStorageKey="minibiblio.patron.token" />;
}
