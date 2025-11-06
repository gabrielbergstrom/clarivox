import React, { useEffect, useState } from "react";
import { View, Text, Button, StyleSheet } from "react-native";
import axios from "axios";

export default function App() {
  const [mensagem, setMensagem] = useState("Conectando...");

  const testarConexao = async () => {
    try {
      const res = await axios.get("http://192.168.0.105:8000");
      setMensagem(res.data.mensagem);
    } catch (err) {
      setMensagem("❌ Erro ao conectar com o backend");
      console.error(err);
    }
  };

  useEffect(() => {
    testarConexao();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Clarivox Mobile</Text>
      <Text style={styles.text}>{mensagem}</Text>
      <Button title="Testar novamente" onPress={testarConexao} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#000" },
  title: { color: "#f4b400", fontSize: 28, fontWeight: "bold", marginBottom: 20 },
  text: { color: "#fff", fontSize: 18, marginBottom: 15 },
});