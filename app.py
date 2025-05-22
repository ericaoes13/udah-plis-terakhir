import streamlit as st
import pandas as pd
import plotly.express as px

# Menambahkan title
st.title("Rekonsiliasi Tarif Invoice dan Ticket Summary")

# Mengunggah file Invoice
invoice_file = st.file_uploader("Unggah File Invoice", type=["xlsx"])
# Mengunggah file Ticket Summary
ticket_file = st.file_uploader("Unggah File Ticket Summary", type=["xlsx"])

if invoice_file and ticket_file:
    # Memuat data dari file yang diupload
    invoice_data = pd.read_excel(invoice_file)
    ticket_data = pd.read_excel(ticket_file)

    # Menampilkan beberapa baris pertama dari kedua file untuk memastikan format data
    st.write("Tabel Invoice:")
    st.dataframe(invoice_data.head())  # Menampilkan beberapa baris pertama data invoice

    st.write("Tabel Ticket Summary:")
    st.dataframe(ticket_data.head())  # Menampilkan beberapa baris pertama data ticket summary

    # Mengelompokkan data berdasarkan "Nomor Invoice" di Ticket Summary dan menjumlahkan "Tarif"
    ticket_summary_grouped = ticket_data.groupby('NOMOR INVOICE')['TARIF'].sum().reset_index()

    # Menggabungkan data berdasarkan "Nomor Invoice" dari Invoice dan hasil agregasi dari Ticket Summary
    merged_data_corrected = pd.merge(invoice_data[['NOMER INVOICE', 'HARGA', 'NAMA CUSTOMER']],
                                      ticket_summary_grouped[['NOMOR INVOICE', 'TARIF']], 
                                      left_on='NOMER INVOICE', right_on='NOMOR INVOICE', how='outer')

    # Membulatkan harga dan tarif untuk memastikan perbandingan yang lebih akurat
    merged_data_corrected['HARGA'] = merged_data_corrected['HARGA'].round(2)
    merged_data_corrected['TARIF'] = merged_data_corrected['TARIF'].round(2)

    # Menambahkan kolom "Match Status" berdasarkan perbandingan harga dan tarif yang dijumlahkan
    merged_data_corrected['Match Status'] = merged_data_corrected.apply(
        lambda x: 'Match' if x['HARGA'] == x['TARIF'] else 'Tidak Match', axis=1)

    # Menampilkan tabel hasil rekonsiliasi
    st.subheader("Hasil Perbandingan Invoice dan Ticket Summary")
    st.dataframe(merged_data_corrected)

    # Menambahkan grafik perbandingan Match vs Tidak Match
    match_counts = merged_data_corrected['Match Status'].value_counts().reset_index()
    match_counts.columns = ['Match Status', 'Jumlah']

    # Membuat pie chart untuk perbandingan
    fig = px.pie(match_counts, values='Jumlah', names='Match Status', title="Perbandingan Match vs Tidak Match")
    st.plotly_chart(fig)

    # Menambahkan grafik batang (bar chart) untuk visualisasi yang lebih jelas
    fig2 = px.bar(match_counts, x='Match Status', y='Jumlah', title="Jumlah Match vs Tidak Match")
    st.plotly_chart(fig2)
